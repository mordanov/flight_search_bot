from pydantic import BaseModel


class SearchProfile(BaseModel):
    slot: int = 1
    name: str = "Profile 1"
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

    def passengers_description(self, lang: str = "en") -> str:
        from app.strings import npl
        adult_word = npl(self.adults, lang, "adult", "adults", "adults") if lang != "ru" else npl(self.adults, lang, "взрослый", "взрослых", "взрослых")
        parts = [f"{self.adults} {adult_word}"]
        if self.children_ages:
            ages = ", ".join(str(a) for a in self.children_ages)
            n = len(self.children_ages)
            if lang == "ru":
                child_word = npl(n, lang, "ребёнок", "ребёнка", "детей")
                parts.append(f"{n} {child_word} (возраст: {ages})")
            else:
                child_word = npl(n, lang, "child", "children", "children")
                parts.append(f"{n} {child_word} (ages: {ages})")
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
