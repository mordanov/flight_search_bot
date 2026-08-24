from app.formatting import (
    _MAX_MESSAGE_LENGTH,
    format_profile,
    format_search_result,
    format_watch_status,
)
from app.models import FlightOption, SearchProfile, SearchResult


def _make_profile(complete: bool = True) -> SearchProfile:
    return SearchProfile(
        origin_airports=["MAD", "VLC"] if complete else [],
        destination_airports=["SVO", "KZN"] if complete else [],
        depart_from="2027-06-24" if complete else None,
        depart_to="2027-07-31" if complete else None,
        trip_length_min=18,
        trip_length_max=23,
        adults=2,
        children_ages=[5, 9],
        max_connections=3,
    )


def _make_option(rank: int, price: float) -> FlightOption:
    return FlightOption(
        rank=rank,
        outbound_date="2027-06-25",
        return_date="2027-07-15",
        origin="MAD",
        destination="KZN",
        airlines=["Air Serbia"],
        outbound_route="MAD-BEG-KZN",
        return_route="KZN-BEG-MAD",
        outbound_connections=1,
        return_connections=1,
        outbound_duration="8h 20m",
        return_duration="9h 05m",
        total_price_eur=price,
        baggage="1x23kg",
        booking_url="https://example.com",
        price_status="bookable",
        notes="",
    )


def test_format_profile_incomplete():
    profile = _make_profile(complete=False)
    text = format_profile(profile)
    assert "not set" in text or "No search profile" in text


def test_format_profile_complete():
    profile = _make_profile(complete=True)
    text = format_profile(profile)
    assert "MAD" in text
    assert "SVO" in text
    assert "2027-06-24" in text


def test_format_search_result_error():
    profile = _make_profile()
    result = SearchResult(
        search_timestamp="2026-08-24T12:00:00Z",
        status="error",
        message="Something went wrong.",
        options=[],
        sources=[],
    )
    text = format_search_result(result, profile)
    assert "error" in text.lower() or "Something went wrong" in text


def test_format_search_result_not_available():
    profile = _make_profile()
    result = SearchResult(
        search_timestamp="2026-08-24T12:00:00Z",
        status="not_available_yet",
        message="2027 fares not yet on sale.",
        options=[],
        sources=[],
    )
    text = format_search_result(result, profile)
    assert "2027 fares" in text


def test_format_search_result_fits_telegram_limit():
    profile = _make_profile()
    # 10 options — worst case for message length
    options = [_make_option(i + 1, 1000.0 + i * 100) for i in range(10)]
    result = SearchResult(
        search_timestamp="2026-08-24T12:00:00Z",
        status="ok",
        message="Found options.",
        options=options,
        sources=["https://example.com"],
    )
    text = format_search_result(result, profile)
    assert len(text) <= _MAX_MESSAGE_LENGTH


def test_format_watch_status_active():
    row = {"watch_enabled": True, "last_watch_run": "2026-08-24 10:00:00+00"}
    text = format_watch_status(row)
    assert "Active" in text or "active" in text.lower()


def test_format_watch_status_inactive():
    row = {"watch_enabled": False, "last_watch_run": None}
    text = format_watch_status(row)
    assert "Inactive" in text or "inactive" in text.lower()
    assert "Never" in text
