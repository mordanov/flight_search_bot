from app.models import FlightOption, SearchProfile, SearchResult


def test_search_profile_is_ready_when_complete():
    profile = SearchProfile(
        origin_airports=["MAD"],
        destination_airports=["SVO"],
        depart_from="2027-06-24",
        depart_to="2027-07-31",
        trip_length_min=18,
        trip_length_max=23,
        adults=2,
        children_ages=[5, 9],
        max_connections=3,
    )
    assert profile.is_ready()


def test_search_profile_not_ready_without_dates():
    profile = SearchProfile(
        origin_airports=["MAD"],
        destination_airports=["SVO"],
        depart_from=None,
        depart_to=None,
        trip_length_min=7,
        trip_length_max=14,
        adults=2,
        children_ages=[],
        max_connections=3,
    )
    assert not profile.is_ready()


def test_search_profile_not_ready_without_origins():
    profile = SearchProfile(
        origin_airports=[],
        destination_airports=["SVO"],
        depart_from="2027-06-24",
        depart_to="2027-07-31",
        trip_length_min=7,
        trip_length_max=14,
        adults=1,
        children_ages=[],
        max_connections=3,
    )
    assert not profile.is_ready()


def test_passengers_description_adults_only():
    profile = SearchProfile(
        origin_airports=[],
        destination_airports=[],
        depart_from=None,
        depart_to=None,
        trip_length_min=7,
        trip_length_max=14,
        adults=2,
        children_ages=[],
        max_connections=3,
    )
    desc = profile.passengers_description()
    assert "2 adults" in desc
    assert "child" not in desc


def test_passengers_description_with_children():
    profile = SearchProfile(
        origin_airports=[],
        destination_airports=[],
        depart_from=None,
        depart_to=None,
        trip_length_min=7,
        trip_length_max=14,
        adults=2,
        children_ages=[5, 9],
        max_connections=3,
    )
    desc = profile.passengers_description()
    assert "2 adults" in desc
    assert "5" in desc
    assert "9" in desc


def test_flight_option_model():
    option = FlightOption(
        rank=1,
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
        total_price_eur=1486.0,
        baggage="1x23kg included",
        booking_url="https://example.com",
        price_status="bookable",
        notes="",
    )
    assert option.total_price_eur == 1486.0
    assert option.origin == "MAD"


def test_search_result_model():
    result = SearchResult(
        search_timestamp="2026-08-24T12:00:00Z",
        status="not_available_yet",
        message="No 2027 fares available yet.",
        options=[],
        sources=[],
    )
    assert result.status == "not_available_yet"
    assert result.options == []
