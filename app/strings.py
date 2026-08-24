STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "access_denied": "⛔ Access denied.",
        "start_welcome": "✈️ *Flight Search Bot*\n\nFind the cheapest flights for any route, configured to your needs.\n\n",
        "no_profile": (
            "No search criteria configured yet.\n\n"
            "Use these commands to set it up:\n"
            "/set\\_origins — departure airports (IATA codes)\n"
            "/set\\_destinations — destination airports\n"
            "/set\\_dates — outbound date window\n"
            "/set\\_trip — trip length range\n"
            "/set\\_passengers — adults and children"
        ),
        "profile_header": "✈️ *{name}*\n",
        "departure_set": "🛫 Departure: {airports}",
        "departure_unset": "🛫 Departure: _(not set)_",
        "destination_set": "🛬 Destination: {airports}",
        "destination_unset": "🛬 Destination: _(not set)_",
        "dates_set": "📅 Outbound window: {from_date} → {to_date}",
        "dates_unset": "📅 Outbound window: _(not set)_",
        "trip_length": "🔄 Trip length: {min}–{max} days",
        "passengers": "👥 Passengers: {desc}",
        "max_connections": "🔀 Max connections: {n}",
        "profile_incomplete_warning": "\n⚠️ Profile incomplete — set origins, destinations, and dates before searching.",
        "profiles_header": "Your profiles:",
        "profiles_add_button": "➕ New",
        "profile_switched": "✅ Switched to: *{name}*",
        "profile_created": "✅ Created *{name}*. Now active.",
        "profile_limit_reached": "⚠️ Max {max} profiles reached. Delete one first.",
        "profile_renamed": "✅ Profile renamed to: *{name}*",
        "rename_usage": "Usage: /rename New Name",
        "profile_deleted": "⭕ *{name}* deleted. Active: *{active}*",
        "cant_delete_last_profile": "⚠️ Cannot delete the last profile.",
        "language_prompt": "Choose language:",
        "language_set_en": "🇬🇧 Language set to English.",
        "language_set_ru": "🇷🇺 Язык изменён на русский.",
        "usage_set_origins": "Usage: /set_origins MAD VLC ALC AGP",
        "usage_set_destinations": "Usage: /set_destinations SVO DME KZN GOJ",
        "usage_set_dates": "Usage: /set_dates YYYY-MM-DD YYYY-MM-DD",
        "usage_set_trip": "Usage: /set_trip MIN_DAYS MAX_DAYS  (e.g. /set_trip 18 23)",
        "usage_set_passengers": (
            "Usage: /set_passengers ADULTS [CHILD_AGES]\n"
            "Examples:\n  /set_passengers 2\n  /set_passengers 2 5,9\n  /set_passengers 1 3"
        ),
        "set_origins_ok": "✅ Departure airports set: {airports}",
        "set_destinations_ok": "✅ Destination airports set: {airports}",
        "set_dates_ok": "✅ Date window set: {from_date} → {to_date}",
        "set_trip_ok": "✅ Trip length set: {min}–{max} days",
        "set_passengers_ok": "✅ Passengers set: {desc}",
        "err_days_not_int": "Days must be integers.",
        "err_min_max_days": "MIN_DAYS must be ≥ 1 and ≤ MAX_DAYS.",
        "err_adults_not_int": "Adults must be an integer; child ages must be comma-separated integers.",
        "err_adults_min": "At least 1 adult required.",
        "search_incomplete": "⚠️ Profile is incomplete. Please set:\n",
        "search_incomplete_add_origins": "/set_origins — departure airports\n",
        "search_incomplete_add_destinations": "/set_destinations — destination airports\n",
        "search_incomplete_add_dates": "/set_dates — date window\n",
        "searching_spinner": "🔍 Searching for flights… This may take a minute or two — the AI is browsing the web for real prices.",
        "watch_need_profile": "⚠️ Complete your search profile before enabling watch.\n/set_origins, /set_destinations, /set_dates",
        "watch_enabled": "✅ Watch enabled. I will search for flights every day at {hour:02d}:{minute:02d} ({tz}) and send you the results.",
        "watch_disabled": "⭕ Watch disabled.",
        "watch_status_active": "🟢 Active",
        "watch_status_inactive": "⭕ Inactive",
        "watch_last_run": "Last run: {dt}",
        "watch_never_run": "Never run",
        "watch_status_full": "👁 *Watch status*\n{status}\n{last}",
        "search_results_header": "✈️ *Flight search results*",
        "search_error": "❌ *Search error*\n",
        "search_sources": "\n\n📚 Sources consulted: {n}",
        "search_truncated": "\n\n_(showing {shown} of {total} options — message size limit)_",
        "search_partial": "\n\n_... (message truncated — too long for Telegram)_",
        "return_route": "Return: {route}",
        "unknown_airline": "Unknown airline",
        "out_ret_duration": "Out: {out_dur} ({out_con} {stop_out}) | Ret: {ret_dur} ({ret_con} {stop_ret})",
        "baggage": "🧳 {desc}",
        "booking_url_label": "🔗 {url}",
        "notes_label": "ℹ️ _{note}_",
        "help_text": (
            "✈️ *Flight Search Bot*\n\n"
            "*Commands:*\n"
            "/start — welcome \\+ profile summary\n"
            "/search — run a search now\n"
            "/profile — show full search profile\n"
            "/language — switch language\n"
            "/profiles — manage search profiles\n\n"
            "*Configure your search:*\n"
            "/set\\_origins MAD VLC ALC — departure airports (IATA)\n"
            "/set\\_destinations SVO DME KZN — destination airports\n"
            "/set\\_dates 2027-06-24 2027-07-31 — outbound date window\n"
            "/set\\_trip 18 23 — trip length min/max in days\n"
            "/set\\_passengers 2 5,9 — adults \\+ comma-separated child ages\n\n"
            "*Profile management:*\n"
            "/profiles — list profiles, switch or create new\n"
            "/rename My Trip — rename active profile\n"
            "/delete\\_profile — delete active profile\n\n"
            "*Monitoring:*\n"
            "/watch — enable daily search (runs every day at 9:00 Europe/Madrid)\n"
            "/watches — show monitoring status\n"
            "/unwatch — disable monitoring\n\n"
            "*Notes:*\n"
            "• Configure origins, destinations, and dates before searching.\n"
            "• The bot uses AI with live web search — a search may take a minute or two.\n"
            "• Prices are sourced from the web and verified by AI. Always confirm on the booking site."
        ),
    },
    "ru": {
        "access_denied": "⛔ Доступ запрещён.",
        "start_welcome": "✈️ *Поиск авиабилетов*\n\nНаходим самые дешёвые рейсы по нужным маршрутам.\n\n",
        "no_profile": (
            "Критерии поиска ещё не заданы.\n\n"
            "Используйте команды:\n"
            "/set\\_origins — аэропорты вылета (коды IATA)\n"
            "/set\\_destinations — аэропорты назначения\n"
            "/set\\_dates — окно дат вылета\n"
            "/set\\_trip — длина поездки\n"
            "/set\\_passengers — взрослые и дети"
        ),
        "profile_header": "✈️ *{name}*\n",
        "departure_set": "🛫 Вылет: {airports}",
        "departure_unset": "🛫 Вылет: _(не указано)_",
        "destination_set": "🛬 Назначение: {airports}",
        "destination_unset": "🛬 Назначение: _(не указано)_",
        "dates_set": "📅 Окно дат: {from_date} → {to_date}",
        "dates_unset": "📅 Окно дат: _(не указано)_",
        "trip_length": "🔄 Длина поездки: {min}–{max} дней",
        "passengers": "👥 Пассажиры: {desc}",
        "max_connections": "🔀 Макс. пересадок: {n}",
        "profile_incomplete_warning": "\n⚠️ Профиль неполный — укажите вылет, назначение и даты перед поиском.",
        "profiles_header": "Ваши профили:",
        "profiles_add_button": "➕ Новый",
        "profile_switched": "✅ Переключено на: *{name}*",
        "profile_created": "✅ Создан *{name}*. Теперь активен.",
        "profile_limit_reached": "⚠️ Достигнут максимум ({max}) профилей. Удалите один, чтобы создать новый.",
        "profile_renamed": "✅ Профиль переименован: *{name}*",
        "rename_usage": "Использование: /rename Новое имя",
        "profile_deleted": "⭕ *{name}* удалён. Активен: *{active}*",
        "cant_delete_last_profile": "⚠️ Нельзя удалить последний профиль.",
        "language_prompt": "Выберите язык:",
        "language_set_en": "🇬🇧 Language set to English.",
        "language_set_ru": "🇷🇺 Язык изменён на русский.",
        "usage_set_origins": "Использование: /set_origins MAD VLC ALC",
        "usage_set_destinations": "Использование: /set_destinations SVO DME KZN",
        "usage_set_dates": "Использование: /set_dates ГГГГ-ММ-ДД ГГГГ-ММ-ДД",
        "usage_set_trip": "Использование: /set_trip МИН МАКС  (например: /set_trip 18 23)",
        "usage_set_passengers": (
            "Использование: /set_passengers ВЗРОСЛЫХ [ВОЗРАСТ_ДЕТЕЙ]\n"
            "Примеры:\n  /set_passengers 2\n  /set_passengers 2 5,9\n  /set_passengers 1 3"
        ),
        "set_origins_ok": "✅ Аэропорты вылета: {airports}",
        "set_destinations_ok": "✅ Аэропорты назначения: {airports}",
        "set_dates_ok": "✅ Даты установлены: {from_date} → {to_date}",
        "set_trip_ok": "✅ Длина поездки: {min}–{max} дней",
        "set_passengers_ok": "✅ Пассажиры: {desc}",
        "err_days_not_int": "Дни должны быть целыми числами.",
        "err_min_max_days": "МИН должно быть ≥ 1 и ≤ МАКС.",
        "err_adults_not_int": "Количество взрослых — целое число; возраст детей — целые числа через запятую.",
        "err_adults_min": "Минимум 1 взрослый.",
        "search_incomplete": "⚠️ Профиль неполный. Укажите:\n",
        "search_incomplete_add_origins": "/set_origins — аэропорты вылета\n",
        "search_incomplete_add_destinations": "/set_destinations — аэропорты назначения\n",
        "search_incomplete_add_dates": "/set_dates — окно дат\n",
        "searching_spinner": "🔍 Ищу рейсы… Это может занять минуту-другую — ИИ обходит сайты для поиска актуальных цен.",
        "watch_need_profile": "⚠️ Заполните профиль поиска перед включением слежения.\n/set_origins, /set_destinations, /set_dates",
        "watch_enabled": "✅ Слежение включено. Буду искать рейсы каждый день в {hour:02d}:{minute:02d} ({tz}) и присылать результаты.",
        "watch_disabled": "⭕ Слежение отключено.",
        "watch_status_active": "🟢 Активно",
        "watch_status_inactive": "⭕ Неактивно",
        "watch_last_run": "Последний запуск: {dt}",
        "watch_never_run": "Ещё не запускалось",
        "watch_status_full": "👁 *Статус слежения*\n{status}\n{last}",
        "search_results_header": "✈️ *Результаты поиска*",
        "search_error": "❌ *Ошибка поиска*\n",
        "search_sources": "\n\n📚 Источников проверено: {n}",
        "search_truncated": "\n\n_(показано {shown} из {total} вариантов — ограничение размера сообщения)_",
        "search_partial": "\n\n_... (сообщение обрезано — слишком длинное для Telegram)_",
        "return_route": "Обратно: {route}",
        "unknown_airline": "Неизвестная авиакомпания",
        "out_ret_duration": "Туда: {out_dur} ({out_con} {stop_out}) | Обратно: {ret_dur} ({ret_con} {stop_ret})",
        "baggage": "🧳 {desc}",
        "booking_url_label": "🔗 {url}",
        "notes_label": "ℹ️ _{note}_",
        "help_text": (
            "✈️ *Поиск авиабилетов*\n\n"
            "*Команды:*\n"
            "/start — приветствие и профиль\n"
            "/search — поиск прямо сейчас\n"
            "/profile — текущий профиль\n"
            "/language — сменить язык\n"
            "/profiles — профили поиска\n\n"
            "*Настройка поиска:*\n"
            "/set\\_origins MAD VLC ALC — аэропорты вылета (IATA)\n"
            "/set\\_destinations SVO DME KZN — аэропорты назначения\n"
            "/set\\_dates 2027-06-24 2027-07-31 — окно дат вылета\n"
            "/set\\_trip 18 23 — мин/макс длина поездки (дней)\n"
            "/set\\_passengers 2 5,9 — взрослые \\+ возраст детей через запятую\n\n"
            "*Управление профилями:*\n"
            "/profiles — список, переключение, создание\n"
            "/rename Название — переименовать активный профиль\n"
            "/delete\\_profile — удалить активный профиль\n\n"
            "*Слежение:*\n"
            "/watch — включить ежедневный поиск (каждый день в 9:00 Europe/Madrid)\n"
            "/watches — статус слежения\n"
            "/unwatch — отключить\n\n"
            "*Примечания:*\n"
            "• Укажите вылет, назначение и даты до начала поиска.\n"
            "• Бот использует ИИ с поиском в интернете — поиск занимает 1–2 минуты.\n"
            "• Цены взяты из сети и проверены ИИ. Всегда уточняйте на сайте бронирования."
        ),
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    s = STRINGS.get(lang, STRINGS["en"]).get(key) or STRINGS["en"].get(key, f"[{key}]")
    return s.format(**kwargs) if kwargs else s


def npl(n: int, lang: str, form_one: str, form_few: str, form_many: str) -> str:
    """Return the appropriate plural form for n."""
    if lang != "ru":
        return form_one if n == 1 else form_many
    abs_n = abs(n)
    if abs_n % 10 == 1 and abs_n % 100 != 11:
        return form_one
    if abs_n % 10 in (2, 3, 4) and abs_n % 100 not in (12, 13, 14):
        return form_few
    return form_many
