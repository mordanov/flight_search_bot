"""
Telegram flight-search bot.

Commands:
  /start         Welcome + show current profile
  /search        Run immediate search
  /profile       Show full search profile
  /language      Switch language (EN/RU)
  /profiles      Manage search profiles
  /rename        Rename active profile
  /delete_profile Delete active profile
  /set_origins   Set departure airports (IATA codes)
  /set_destinations  Set destination airports
  /set_dates     Set outbound date window
  /set_trip      Set trip length range (min/max days)
  /set_passengers Set passengers (adults + child ages)
  /watch         Enable periodic monitoring
  /watches       Show watch status
  /unwatch       Disable monitoring
  /help          Help

Required env vars:
  TELEGRAM_BOT_TOKEN
  OPENAI_API_KEY
  DATABASE_URL (PostgreSQL connection string)
Optional:
  OPENAI_MODEL (default: gpt-4o)
  OPENAI_SEARCH_CONTEXT_SIZE (default: high)
  WATCH_SEND_HOUR (default: 9)
  WATCH_SEND_MINUTE (default: 0)
  WATCH_TIMEZONE (default: Europe/Madrid)
  ALLOWED_TELEGRAM_USER_IDS (comma-separated; empty = allow all)
  MAX_PROFILES_PER_USER (default: 5)
"""

import datetime
import logging
from zoneinfo import ZoneInfo

from telegram import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

import app.db as db
from app.config import config
from app.formatting import format_profile, format_search_result, format_watch_status
from app.models import SearchProfile
from app.search import run_search
from app.strings import t

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_BOT_COMMANDS = [
    BotCommand("start", "Welcome + show search profile"),
    BotCommand("search", "Run a flight search now"),
    BotCommand("profile", "Show your search profile"),
    BotCommand("language", "Switch language / Сменить язык"),
    BotCommand("profiles", "Manage search profiles"),
    BotCommand("rename", "Rename active profile"),
    BotCommand("delete_profile", "Delete active profile"),
    BotCommand("set_origins", "Set departure airports, e.g. /set_origins MAD VLC"),
    BotCommand("set_destinations", "Set destination airports, e.g. /set_destinations SVO DME"),
    BotCommand("set_dates", "Set outbound date window, e.g. /set_dates 2027-06-24 2027-07-31"),
    BotCommand("set_trip", "Set trip length range, e.g. /set_trip 18 23"),
    BotCommand("set_passengers", "Set passengers, e.g. /set_passengers 2 5,9"),
    BotCommand("watch", "Enable daily flight monitoring"),
    BotCommand("watches", "Show monitoring status"),
    BotCommand("unwatch", "Disable monitoring"),
    BotCommand("help", "Show command reference"),
]


def _is_allowed(user_id: int) -> bool:
    allowed = config.allowed_user_ids()
    return not allowed or user_id in allowed


async def _require_auth(update: Update) -> bool:
    if not _is_allowed(update.effective_user.id):
        await update.effective_message.reply_text("⛔ Access denied.")
        return False
    return True


def _get_profile(row: dict) -> SearchProfile:
    return db.row_to_profile(row)


def _lang(row: dict) -> str:
    return row.get("language", "en")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    profile = _get_profile(row)
    await update.effective_message.reply_text(
        t("start_welcome", lang) + format_profile(profile, lang),
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    await update.effective_message.reply_text(t("help_text", _lang(row)), parse_mode="Markdown")


async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    profile = _get_profile(row)
    await update.effective_message.reply_text(format_profile(profile, lang), parse_mode="Markdown")


async def cmd_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
    ]])
    await update.effective_message.reply_text(t("language_prompt", lang), reply_markup=keyboard)


async def cb_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    lang_code = query.data[len("lang_"):]
    db.set_language(chat_id, lang_code)
    key = "language_set_en" if lang_code == "en" else "language_set_ru"
    await query.edit_message_text(t(key, lang_code))


async def cmd_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    active_slot = row.get("active_profile_slot", 1)
    profiles = db.get_all_profiles(update.effective_chat.id)
    buttons = []
    for p in profiles:
        label = f"🔵 {p['name']}" if p["slot"] == active_slot else p["name"]
        buttons.append([InlineKeyboardButton(label, callback_data=f"profile_select_{p['slot']}")])
    if len(profiles) < config.max_profiles_per_user:
        buttons.append([InlineKeyboardButton(t("profiles_add_button", lang), callback_data="profile_new")])
    keyboard = InlineKeyboardMarkup(buttons)
    await update.effective_message.reply_text(t("profiles_header", lang), reply_markup=keyboard)


async def cb_profiles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    row = db.get_or_create_user(chat_id)
    lang = _lang(row)

    if query.data == "profile_new":
        profiles = db.get_all_profiles(chat_id)
        if len(profiles) >= config.max_profiles_per_user:
            await query.edit_message_text(t("profile_limit_reached", lang, max=config.max_profiles_per_user))
            return
        existing_slots = {p["slot"] for p in profiles}
        slot = next(s for s in range(1, config.max_profiles_per_user + 1) if s not in existing_slots)
        name = f"Profile {slot}"
        db.create_profile(chat_id, slot, name)
        db.set_active_profile(chat_id, slot)
        await query.edit_message_text(t("profile_created", lang, name=name), parse_mode="Markdown")
        return

    if query.data.startswith("profile_select_"):
        slot = int(query.data[len("profile_select_"):])
        active_slot = row.get("active_profile_slot", 1)
        if slot == active_slot:
            return
        db.set_active_profile(chat_id, slot)
        profiles = db.get_all_profiles(chat_id)
        name = next((p["name"] for p in profiles if p["slot"] == slot), f"Profile {slot}")
        await query.edit_message_text(t("profile_switched", lang, name=name), parse_mode="Markdown")


async def cmd_rename(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    if not context.args:
        await update.effective_message.reply_text(t("rename_usage", lang))
        return
    name = " ".join(context.args).strip()
    slot = row.get("active_profile_slot", 1)
    db.update_profile(update.effective_chat.id, slot, name=name)
    await update.effective_message.reply_text(t("profile_renamed", lang, name=name), parse_mode="Markdown")


async def cmd_delete_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    profiles = db.get_all_profiles(update.effective_chat.id)
    if len(profiles) <= 1:
        await update.effective_message.reply_text(t("cant_delete_last_profile", lang))
        return
    active_slot = row.get("active_profile_slot", 1)
    deleted_name = next((p["name"] for p in profiles if p["slot"] == active_slot), f"Profile {active_slot}")
    db.delete_profile(update.effective_chat.id, active_slot)
    remaining = db.get_all_profiles(update.effective_chat.id)
    new_slot = remaining[0]["slot"]
    new_name = remaining[0]["name"]
    db.set_active_profile(update.effective_chat.id, new_slot)
    await update.effective_message.reply_text(
        t("profile_deleted", lang, name=deleted_name, active=new_name),
        parse_mode="Markdown",
    )


async def cmd_set_origins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    if not context.args:
        await update.effective_message.reply_text(t("usage_set_origins", lang))
        return
    airports = [a.upper() for a in context.args]
    db.update_user_profile(update.effective_chat.id, origin_airports=airports)
    await update.effective_message.reply_text(t("set_origins_ok", lang, airports=", ".join(airports)))


async def cmd_set_destinations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    if not context.args:
        await update.effective_message.reply_text(t("usage_set_destinations", lang))
        return
    airports = [a.upper() for a in context.args]
    db.update_user_profile(update.effective_chat.id, destination_airports=airports)
    await update.effective_message.reply_text(t("set_destinations_ok", lang, airports=", ".join(airports)))


async def cmd_set_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    if not context.args or len(context.args) != 2:
        await update.effective_message.reply_text(t("usage_set_dates", lang))
        return
    from_date, to_date = context.args[0], context.args[1]
    try:
        datetime.date.fromisoformat(from_date)
        datetime.date.fromisoformat(to_date)
    except ValueError:
        await update.effective_message.reply_text(t("err_invalid_date", lang))
        return
    db.update_user_profile(update.effective_chat.id, depart_from=from_date, depart_to=to_date)
    await update.effective_message.reply_text(t("set_dates_ok", lang, from_date=from_date, to_date=to_date))


async def cmd_set_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    if not context.args or len(context.args) != 2:
        await update.effective_message.reply_text(t("usage_set_trip", lang))
        return
    try:
        min_days = int(context.args[0])
        max_days = int(context.args[1])
    except ValueError:
        await update.effective_message.reply_text(t("err_days_not_int", lang))
        return
    if min_days < 1 or max_days < min_days:
        await update.effective_message.reply_text(t("err_min_max_days", lang))
        return
    db.update_user_profile(update.effective_chat.id, trip_length_min=min_days, trip_length_max=max_days)
    await update.effective_message.reply_text(t("set_trip_ok", lang, min=min_days, max=max_days))


async def cmd_set_passengers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    if not context.args:
        await update.effective_message.reply_text(t("usage_set_passengers", lang))
        return
    try:
        adults = int(context.args[0])
        children_ages: list[int] = []
        if len(context.args) > 1:
            children_ages = [int(a) for a in context.args[1].split(",") if a.strip()]
    except ValueError:
        await update.effective_message.reply_text(t("err_adults_not_int", lang))
        return
    if adults < 1:
        await update.effective_message.reply_text(t("err_adults_min", lang))
        return
    db.update_user_profile(update.effective_chat.id, adults=adults, children_ages=children_ages)
    sp = SearchProfile(
        origin_airports=[],
        destination_airports=[],
        depart_from=None,
        depart_to=None,
        trip_length_min=0,
        trip_length_max=0,
        adults=adults,
        children_ages=children_ages,
        max_connections=3,
    )
    await update.effective_message.reply_text(t("set_passengers_ok", lang, desc=sp.passengers_description(lang)))


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    profile = _get_profile(row)
    if not profile.is_ready():
        await update.effective_message.reply_text(
            t("search_incomplete", lang)
            + (t("search_incomplete_add_origins", lang) if not profile.origin_airports else "")
            + (t("search_incomplete_add_destinations", lang) if not profile.destination_airports else "")
            + (t("search_incomplete_add_dates", lang) if not profile.depart_from else ""),
        )
        return
    await update.effective_message.reply_text(t("searching_spinner", lang))
    result = await run_search(profile, lang)
    text = format_search_result(result, profile, lang)
    await update.effective_message.reply_text(text, parse_mode="Markdown")


async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    profile = _get_profile(row)
    if not profile.is_ready():
        await update.effective_message.reply_text(t("watch_need_profile", lang))
        return
    slot = row.get("active_profile_slot", 1)
    db.set_watch(update.effective_chat.id, slot, enabled=True)
    tz = config.watch_timezone
    hour = config.watch_send_hour
    minute = config.watch_send_minute
    await update.effective_message.reply_text(t("watch_enabled", lang, hour=hour, minute=minute, tz=tz))


async def cmd_watches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    await update.effective_message.reply_text(format_watch_status(row, _lang(row)), parse_mode="Markdown")


async def cmd_unwatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    lang = _lang(row)
    slot = row.get("active_profile_slot", 1)
    db.set_watch(update.effective_chat.id, slot, enabled=False)
    await update.effective_message.reply_text(t("watch_disabled", lang))


async def _watch_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    rows = db.get_all_watch_profiles()
    logger.info("Watch job: %d subscribed profile(s)", len(rows))
    for row in rows:
        chat_id = row["chat_id"]
        slot = row["slot"]
        lang = row.get("language", "en")
        profile = _get_profile(row)
        if not profile.is_ready():
            logger.warning("Watch: chat %d slot %d has incomplete profile, skipping", chat_id, slot)
            continue
        try:
            result = await run_search(profile, lang)
            text = format_search_result(result, profile, lang)
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
            db.mark_watch_run(chat_id, slot)
        except Exception as exc:
            logger.exception("Watch job failed for chat %d slot %d: %s", chat_id, slot, exc)


async def _post_init(application: Application) -> None:
    db.init_schema()
    await application.bot.set_my_commands(_BOT_COMMANDS)
    logger.info("Schema initialised and bot commands registered")


def main() -> None:
    app = (
        Application.builder()
        .token(config.telegram_bot_token)
        .post_init(_post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("profile", cmd_profile))
    app.add_handler(CommandHandler("language", cmd_language))
    app.add_handler(CommandHandler("profiles", cmd_profiles))
    app.add_handler(CommandHandler("rename", cmd_rename))
    app.add_handler(CommandHandler("delete_profile", cmd_delete_profile))
    app.add_handler(CommandHandler("set_origins", cmd_set_origins))
    app.add_handler(CommandHandler("set_destinations", cmd_set_destinations))
    app.add_handler(CommandHandler("set_dates", cmd_set_dates))
    app.add_handler(CommandHandler("set_trip", cmd_set_trip))
    app.add_handler(CommandHandler("set_passengers", cmd_set_passengers))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("watch", cmd_watch))
    app.add_handler(CommandHandler("watches", cmd_watches))
    app.add_handler(CommandHandler("unwatch", cmd_unwatch))
    app.add_handler(CallbackQueryHandler(cb_language, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(cb_profiles, pattern="^profile_"))

    send_time = datetime.time(
        hour=config.watch_send_hour,
        minute=config.watch_send_minute,
        tzinfo=ZoneInfo(config.watch_timezone),
    )
    app.job_queue.run_daily(_watch_job, time=send_time, name="watch_job")

    logger.info("Starting bot (polling)…")
    app.run_polling()


if __name__ == "__main__":
    main()
