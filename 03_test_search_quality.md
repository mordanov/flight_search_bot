Now audit the actual flight-search prompt and search algorithm as a travel-search specialist.

The target is:
- 2 adults
- children ages 5 and 9
- departures MAD/VLC/ALC/AGP/SVQ
- destinations MOW (SVO/DME/VKO), KZN, GOJ
- outbound 2027-06-24 through 2027-07-31
- return 18–23 days after outbound
- maximum 3 connections per direction
- lowest total family price

Check whether the implementation can accidentally:
- search only one date
- search only one airport
- rank by adult price instead of total family price
- ignore child fares
- mix one-way and round-trip prices incorrectly
- report a price without taxes
- report a price without required baggage when comparing fares
- claim a future fare that is not actually bookable
- confuse schedule availability with fare availability
- miss Kazan or Nizhny Novgorod
- miss useful transit hubs
- incorrectly count connections
- treat separate tickets as one protected itinerary

Improve the prompt and code where necessary.

The agent should discover cheap candidate itineraries and then verify them instead of performing an uncontrolled number of searches.

The final result must clearly distinguish:
1. verified/bookable price
2. published schedule but no bookable price found
3. unavailable/future information

Run tests after changes.
