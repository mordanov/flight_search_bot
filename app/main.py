"""
Telegram flight-search bot.

Commands:
  /start         Welcome + show current profile
  /search        Run immediate search
  /profile       Show full search profile
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
"""

import datetime
import logging
from zoneinfo import ZoneInfo

from telegram import BotCommand, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

import app.db as db
from app.config import config
from app.formatting import format_profile, format_search_result, format_watch_status
from app.models import SearchProfile
from app.search import run_search

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_BOT_COMMANDS = [
    BotCommand("start", "Welcome + show search profile"),
    BotCommand("search", "Run a flight search now"),
    BotCommand("profile", "Show your search profile"),
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

_HELP_TEXT = """
✈️ *Flight Search Bot*

*Commands:*
/start — welcome + profile summary
/search — run a search now
/profile — show full search profile

*Configure your search:*
/set\\_origins MAD VLC ALC — departure airports (IATA)
/set\\_destinations SVO DME KZN — destination airports
/set\\_dates 2027-06-24 2027-07-31 — outbound date window
/set\\_trip 18 23 — trip length min/max in days
/set\\_passengers 2 5,9 — adults + comma-separated child ages

*Monitoring:*
/watch — enable daily search (runs every day at 9:00 Europe/Madrid)
/watches — show monitoring status
/unwatch — disable monitoring

*Notes:*
• Configure origins, destinations, and dates before searching.
• The bot uses AI with live web search — a search may take a minute or two.
• Prices are sourced from the web and verified by AI. Always confirm on the booking site.
""".strip()


def _is_allowed(user_id: int) -> bool:
    allowed = config.allowed_user_ids()
    return not allowed or user_id in allowed


async def _require_auth(update: Update) -> bool:
    if not _is_allowed(update.effective_user.id):
        await update.message.reply_text("⛔ Access denied.")
        return False
    return True


def _get_profile(row: dict) -> SearchProfile:
    return db.row_to_profile(row)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    profile = _get_profile(row)
    welcome = "✈️ *Flight Search Bot*\n\nFind the cheapest flights for any route, configured to your needs.\n\n"
    await update.message.reply_text(
        welcome + format_profile(profile), parse_mode="Markdown"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    await update.message.reply_text(_HELP_TEXT, parse_mode="Markdown")


async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    profile = _get_profile(row)
    await update.message.reply_text(format_profile(profile), parse_mode="Markdown")


async def cmd_set_origins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /set_origins MAD VLC ALC AGP")
        return
    airports = [a.upper() for a in context.args]
    db.get_or_create_user(update.effective_chat.id)
    db.update_user_profile(update.effective_chat.id, origin_airports=airports)
    await update.message.reply_text(f"✅ Departure airports set: {', '.join(airports)}")


async def cmd_set_destinations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /set_destinations SVO DME KZN GOJ")
        return
    airports = [a.upper() for a in context.args]
    db.get_or_create_user(update.effective_chat.id)
    db.update_user_profile(update.effective_chat.id, destination_airports=airports)
    await update.message.reply_text(f"✅ Destination airports set: {', '.join(airports)}")


async def cmd_set_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    if not context.args or len(context.args) != 2:
        await update.message.reply_text("Usage: /set_dates YYYY-MM-DD YYYY-MM-DD")
        return
    from_date, to_date = context.args[0], context.args[1]
    db.get_or_create_user(update.effective_chat.id)
    db.update_user_profile(update.effective_chat.id, depart_from=from_date, depart_to=to_date)
    await update.message.reply_text(f"✅ Date window set: {from_date} → {to_date}")


async def cmd_set_trip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    if not context.args or len(context.args) != 2:
        await update.message.reply_text("Usage: /set_trip MIN_DAYS MAX_DAYS  (e.g. /set_trip 18 23)")
        return
    try:
        min_days = int(context.args[0])
        max_days = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Days must be integers.")
        return
    if min_days < 1 or max_days < min_days:
        await update.message.reply_text("MIN_DAYS must be ≥ 1 and ≤ MAX_DAYS.")
        return
    db.get_or_create_user(update.effective_chat.id)
    db.update_user_profile(update.effective_chat.id, trip_length_min=min_days, trip_length_max=max_days)
    await update.message.reply_text(f"✅ Trip length set: {min_days}–{max_days} days")


async def cmd_set_passengers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /set_passengers ADULTS [CHILD_AGES]\n"
            "Examples:\n  /set_passengers 2\n  /set_passengers 2 5,9\n  /set_passengers 1 3"
        )
        return
    try:
        adults = int(context.args[0])
        children_ages: list[int] = []
        if len(context.args) > 1:
            children_ages = [int(a) for a in context.args[1].split(",") if a.strip()]
    except ValueError:
        await update.message.reply_text("Adults must be an integer; child ages must be comma-separated integers.")
        return
    if adults < 1:
        await update.message.reply_text("At least 1 adult required.")
        return
    db.get_or_create_user(update.effective_chat.id)
    db.update_user_profile(update.effective_chat.id, adults=adults, children_ages=children_ages)
    from app.models import SearchProfile as SP
    sp = SP(
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
    await update.message.reply_text(f"✅ Passengers set: {sp.passengers_description()}")


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    profile = _get_profile(row)
    if not profile.is_ready():
        await update.message.reply_text(
            "⚠️ Profile is incomplete. Please set:\n"
            + ("/set\\_origins — departure airports\n" if not profile.origin_airports else "")
            + ("/set\\_destinations — destination airports\n" if not profile.destination_airports else "")
            + ("/set\\_dates — date window\n" if not profile.depart_from else ""),
            parse_mode="Markdown",
        )
        return
    await update.message.reply_text(
        "🔍 Searching for flights… This may take a minute or two — the AI is browsing the web for real prices.",
        parse_mode="Markdown",
    )
    result = await run_search(profile)
    text = format_search_result(result, profile)
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_watch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    profile = _get_profile(row)
    if not profile.is_ready():
        await update.message.reply_text(
            "⚠️ Complete your search profile before enabling watch.\n/set_origins, /set_destinations, /set_dates"
        )
        return
    db.set_watch(update.effective_chat.id, enabled=True)
    tz = config.watch_timezone
    hour = config.watch_send_hour
    minute = config.watch_send_minute
    await update.message.reply_text(
        f"✅ Watch enabled. I will search for flights every day at {hour:02d}:{minute:02d} ({tz}) and send you the results."
    )


async def cmd_watches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    row = db.get_or_create_user(update.effective_chat.id)
    await update.message.reply_text(format_watch_status(row), parse_mode="Markdown")


async def cmd_unwatch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _require_auth(update):
        return
    db.get_or_create_user(update.effective_chat.id)
    db.set_watch(update.effective_chat.id, enabled=False)
    await update.message.reply_text("⭕ Watch disabled.")


async def _watch_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scheduled job: search for all users with watch enabled and send results."""
    users = db.get_all_watch_users()
    logger.info("Watch job: %d subscribed user(s)", len(users))
    for row in users:
        chat_id = row["chat_id"]
        profile = _get_profile(row)
        if not profile.is_ready():
            logger.warning("Watch: user %d has incomplete profile, skipping", chat_id)
            continue
        try:
            result = await run_search(profile)
            text = format_search_result(result, profile)
            await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
            db.mark_watch_run(chat_id)
        except Exception as exc:
            logger.exception("Watch job failed for chat %d: %s", chat_id, exc)


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
    app.add_handler(CommandHandler("set_origins", cmd_set_origins))
    app.add_handler(CommandHandler("set_destinations", cmd_set_destinations))
    app.add_handler(CommandHandler("set_dates", cmd_set_dates))
    app.add_handler(CommandHandler("set_trip", cmd_set_trip))
    app.add_handler(CommandHandler("set_passengers", cmd_set_passengers))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("watch", cmd_watch))
    app.add_handler(CommandHandler("watches", cmd_watches))
    app.add_handler(CommandHandler("unwatch", cmd_unwatch))

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
