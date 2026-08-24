from app.models import FlightOption, SearchProfile, SearchResult
from app.strings import npl, t

_MEDAL = ["🥇", "🥈", "🥉"]
_MAX_MESSAGE_LENGTH = 4000  # Telegram limit is 4096; leave headroom


def _esc(text: str) -> str:
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, "\\" + ch)
    return text


def format_profile(profile: SearchProfile, lang: str = "en") -> str:
    header = t("profile_header", lang, name=_esc(profile.name))
    if not any([profile.origin_airports, profile.destination_airports]):
        return header + t("no_profile", lang)
    lines = [header]
    if profile.origin_airports:
        lines.append(t("departure_set", lang, airports=" / ".join(_esc(a) for a in profile.origin_airports)))
    else:
        lines.append(t("departure_unset", lang))
    if profile.destination_airports:
        lines.append(t("destination_set", lang, airports=" / ".join(_esc(a) for a in profile.destination_airports)))
    else:
        lines.append(t("destination_unset", lang))
    if profile.depart_from and profile.depart_to:
        lines.append(t("dates_set", lang, from_date=_esc(profile.depart_from), to_date=_esc(profile.depart_to)))
    else:
        lines.append(t("dates_unset", lang))
    lines.append(t("trip_length", lang, min=profile.trip_length_min, max=profile.trip_length_max))
    lines.append(t("passengers", lang, desc=profile.passengers_description(lang)))
    lines.append(t("max_connections", lang, n=profile.max_connections))
    if not profile.is_ready():
        lines.append(t("profile_incomplete_warning", lang))
    return "\n".join(lines)


def _format_option(opt: FlightOption, index: int, lang: str = "en") -> str:
    medal = _MEDAL[index] if index < len(_MEDAL) else f"#{opt.rank}"
    status_icon = {"bookable": "✅", "schedule_only": "📋", "not_available_yet": "❌"}.get(
        opt.price_status, "❓"
    )
    airlines = ", ".join(_esc(a) for a in opt.airlines) if opt.airlines else t("unknown_airline", lang)
    stop_out = npl(opt.outbound_connections, lang, "stop", "stops", "stops") if lang != "ru" else npl(opt.outbound_connections, lang, "пересадка", "пересадки", "пересадок")
    stop_ret = npl(opt.return_connections, lang, "stop", "stops", "stops") if lang != "ru" else npl(opt.return_connections, lang, "пересадка", "пересадки", "пересадок")
    lines = [
        f"{medal} *€{opt.total_price_eur:,.0f} total* {status_icon}",
        f"{_esc(opt.outbound_date)} → {_esc(opt.return_date)}",
        f"{_esc(opt.outbound_route)}",
        t("return_route", lang, route=_esc(opt.return_route)),
        airlines,
        t("out_ret_duration", lang,
          out_dur=_esc(opt.outbound_duration), out_con=opt.outbound_connections, stop_out=stop_out,
          ret_dur=_esc(opt.return_duration), ret_con=opt.return_connections, stop_ret=stop_ret),
        t("baggage", lang, desc=_esc(opt.baggage)),
    ]
    if opt.booking_url and opt.booking_url not in ("not available", ""):
        lines.append(t("booking_url_label", lang, url=_esc(opt.booking_url)))
    if opt.notes:
        lines.append(t("notes_label", lang, note=_esc(opt.notes)))
    return "\n".join(lines)


def format_search_result(result: SearchResult, profile: SearchProfile, lang: str = "en") -> str:
    header_parts = [
        t("search_results_header", lang),
        t("passengers", lang, desc=profile.passengers_description(lang)),
        f"📅 {profile.depart_from} → {profile.depart_to} | "
        f"Trip: {profile.trip_length_min}–{profile.trip_length_max} days",
        f"🛫 {' / '.join(profile.origin_airports)} → {' / '.join(profile.destination_airports)}",
    ]
    header = "\n".join(header_parts)

    if result.status == "error":
        return f"{header}\n\n{t('search_error', lang)}{result.message}"

    if result.status == "not_available_yet" or not result.options:
        return f"{header}\n\n⚠️ *{result.message}*"

    option_blocks = [
        _format_option(opt, i, lang) for i, opt in enumerate(result.options[:10])
    ]

    sources_text = t("search_sources", lang, n=len(result.sources)) if result.sources else ""

    full = header + "\n\n" + "\n\n─────\n\n".join(option_blocks) + sources_text

    if len(full) > _MAX_MESSAGE_LENGTH:
        for n in range(len(option_blocks) - 1, 0, -1):
            trimmed = (
                header
                + "\n\n"
                + "\n\n─────\n\n".join(option_blocks[:n])
                + t("search_truncated", lang, shown=n, total=len(result.options))
                + sources_text
            )
            if len(trimmed) <= _MAX_MESSAGE_LENGTH:
                return trimmed
        return header + "\n\n" + option_blocks[0] + t("search_partial", lang)

    return full


def format_watch_status(row: dict, lang: str = "en") -> str:
    enabled = row.get("watch_enabled", False)
    last_run = row.get("last_watch_run")
    status = t("watch_status_active", lang) if enabled else t("watch_status_inactive", lang)
    last = t("watch_last_run", lang, dt=last_run) if last_run else t("watch_never_run", lang)
    return t("watch_status_full", lang, status=status, last=last)
