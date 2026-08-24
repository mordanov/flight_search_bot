from pydantic import BaseModel


class SearchProfile(BaseModel):
    origin_airports: list[str]
    destination_airports: list[str]
    depart_from: str | None
    depart_to: str | None
    trip_length_min: int
    trip_length_max: int
    adults: int
    children_ages: list[int]
    max_connections: int

    def is_ready(self) -> bool:
        return bool(
            self.origin_airports
            and self.destination_airports
            and self.depart_from
            and self.depart_to
        )

    def passengers_description(self) -> str:
        parts = [f"{self.adults} adult{'s' if self.adults != 1 else ''}"]
        if self.children_ages:
            ages = ", ".join(str(a) for a in self.children_ages)
            n = len(self.children_ages)
            parts.append(f"{n} child{'ren' if n != 1 else ''} (ages: {ages})")
        return " + ".join(parts)


class FlightOption(BaseModel):
    rank: int
    outbound_date: str
    return_date: str
    origin: str
    destination: str
    airlines: list[str]
    outbound_route: str
    return_route: str
    outbound_connections: int
    return_connections: int
    outbound_duration: str
    return_duration: str
    total_price_eur: float
    baggage: str
    booking_url: str
    price_status: str  # "bookable" | "schedule_only" | "not_available_yet"
    notes: str


class SearchResult(BaseModel):
    search_timestamp: str
    status: str  # "ok" | "not_available_yet" | "error"
    message: str
    options: list[FlightOption]
    sources: list[str]
