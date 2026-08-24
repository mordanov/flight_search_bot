from app.models import FlightOption, SearchProfile, SearchResult

_MEDAL = ["🥇", "🥈", "🥉"]


def _esc(text: str) -> str:
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, "\\" + ch)
    return text
_MAX_MESSAGE_LENGTH = 4000  # Telegram limit is 4096; leave headroom
_TRUNCATION_NOTE = "\n\n_... (message truncated — too long for Telegram)_"


def format_profile(profile: SearchProfile) -> str:
    if not any([profile.origin_airports, profile.destination_airports]):
        return (
            "No search profile configured yet.\n\n"
            "Use these commands to set it up:\n"
            "/set_origins — departure airports (IATA codes)\n"
            "/set_destinations — destination airports\n"
            "/set_dates — outbound date window\n"
            "/set_trip — trip length range\n"
            "/set_passengers — adults and children"
        )
    lines = ["✈️ *Current search profile*\n"]
    if profile.origin_airports:
        lines.append(f"🛫 Departure: {' / '.join(_esc(a) for a in profile.origin_airports)}")
    else:
        lines.append("🛫 Departure: _(not set)_")
    if profile.destination_airports:
        lines.append(f"🛬 Destination: {' / '.join(_esc(a) for a in profile.destination_airports)}")
    else:
        lines.append("🛬 Destination: _(not set)_")
    if profile.depart_from and profile.depart_to:
        lines.append(f"📅 Outbound window: {_esc(profile.depart_from)} → {_esc(profile.depart_to)}")
    else:
        lines.append("📅 Outbound window: _(not set)_")
    lines.append(
        f"🔄 Trip length: {profile.trip_length_min}–{profile.trip_length_max} days"
    )
    lines.append(f"👥 Passengers: {profile.passengers_description()}")
    lines.append(f"🔀 Max connections: {profile.max_connections}")
    if not profile.is_ready():
        lines.append("\n⚠️ Profile incomplete — set origins, destinations, and dates before searching.")
    return "\n".join(lines)


def _format_option(opt: FlightOption, index: int) -> str:
    medal = _MEDAL[index] if index < len(_MEDAL) else f"#{opt.rank}"
    status_icon = {"bookable": "✅", "schedule_only": "📋", "not_available_yet": "❌"}.get(
        opt.price_status, "❓"
    )
    airlines = ", ".join(_esc(a) for a in opt.airlines) if opt.airlines else "Unknown airline"
    lines = [
        f"{medal} *€{opt.total_price_eur:,.0f} total* {status_icon}",
        f"{_esc(opt.outbound_date)} → {_esc(opt.return_date)}",
        f"{_esc(opt.outbound_route)}",
        f"Return: {_esc(opt.return_route)}",
        f"{airlines}",
        f"Out: {_esc(opt.outbound_duration)} ({opt.outbound_connections} stop{'s' if opt.outbound_connections != 1 else ''})"
        f" | Ret: {_esc(opt.return_duration)} ({opt.return_connections} stop{'s' if opt.return_connections != 1 else ''})",
        f"🧳 {_esc(opt.baggage)}",
    ]
    if opt.booking_url and opt.booking_url not in ("not available", ""):
        lines.append(f"🔗 {_esc(opt.booking_url)}")
    if opt.notes:
        lines.append(f"ℹ️ _{_esc(opt.notes)}_")
    return "\n".join(lines)


def format_search_result(result: SearchResult, profile: SearchProfile) -> str:
    header_parts = [
        "✈️ *Flight search results*",
        f"👥 {profile.passengers_description()}",
        f"📅 {profile.depart_from} → {profile.depart_to} | "
        f"Trip: {profile.trip_length_min}–{profile.trip_length_max} days",
        f"🛫 {' / '.join(profile.origin_airports)} → {' / '.join(profile.destination_airports)}",
    ]
    header = "\n".join(header_parts)

    if result.status == "error":
        return f"{header}\n\n❌ *Search error*\n{result.message}"

    if result.status == "not_available_yet" or not result.options:
        return f"{header}\n\n⚠️ *{result.message}*"

    option_blocks = [
        _format_option(opt, i) for i, opt in enumerate(result.options[:10])
    ]

    sources_text = ""
    if result.sources:
        sources_text = "\n\n📚 Sources consulted: " + str(len(result.sources))

    full = header + "\n\n" + "\n\n─────\n\n".join(option_blocks) + sources_text

    if len(full) > _MAX_MESSAGE_LENGTH:
        # Trim options one by one until it fits
        for n in range(len(option_blocks) - 1, 0, -1):
            trimmed = (
                header
                + "\n\n"
                + "\n\n─────\n\n".join(option_blocks[:n])
                + f"\n\n_(showing {n} of {len(result.options)} options — message size limit)_"
                + sources_text
            )
            if len(trimmed) <= _MAX_MESSAGE_LENGTH:
                return trimmed
        # Absolute fallback: just the header and first option
        return header + "\n\n" + option_blocks[0] + _TRUNCATION_NOTE

    return full


def format_watch_status(row: dict) -> str:
    enabled = row.get("watch_enabled", False)
    last_run = row.get("last_watch_run")
    status = "🟢 Active" if enabled else "⭕ Inactive"
    last = f"Last run: {last_run}" if last_run else "Never run"
    return f"👁 *Watch status*\n{status}\n{last}"
