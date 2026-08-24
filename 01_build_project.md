Create a complete, production-ready Telegram bot in Python for finding the cheapest family flights.

Do not just explain the solution. Create all required project files and implementation code.

## Goal

The bot searches current online flight schedules and prices using the OpenAI Responses API with the built-in web_search tool.

The bot must find the cheapest round-trip options for:

Passengers:
- 2 adults
- 2 children: ages 5 and 9

Departure airports:
- MAD — Madrid
- VLC — Valencia
- ALC — Alicante
- AGP — Malaga
- SVQ — Seville

Destination airports:
- Moscow: SVO, DME, VKO
- KZN — Kazan
- GOJ — Nizhny Novgorod

Outbound date:
- any date from 2027-06-24 through 2027-07-31 inclusive

Return date:
- 18 to 23 calendar days after the outbound date

Maximum:
- 3 connections in each direction

Primary optimization criterion:
- lowest TOTAL price for all 4 passengers
- not per-person price

## Important flight-search rules

Use CURRENT online information.

Never invent prices, schedules, routes or availability.

A price is real only when supported by a current online source. Clearly distinguish published/bookable prices from schedule-only information.

Search broadly across airlines, flight search engines, different transit hubs, all departure airports, and all destination airports.

Do not assume Moscow is cheaper than Kazan or Nizhny Novgorod.

Consider routes through relevant hubs such as Istanbul, Belgrade, Cairo, Dubai, Abu Dhabi, Doha, Yerevan, Tbilisi, Baku, and any other hubs discovered during the search. Do not limit the search to these hubs.

Prefer a single-ticket itinerary.

Separate tickets may be considered only if:
1. the total price can be established reliably;
2. the itinerary is realistic;
3. the result is clearly marked as separate tickets;
4. baggage and self-transfer/airport-transfer risks are mentioned.

Include mandatory taxes and fees.
Include checked baggage information when available.

Important:
- A flight that is not yet on sale is not a bookable price.
- If 2027 fares are not available, say so explicitly.
- Never convert old/current prices into predictions for 2027.
- Never claim a route operates on a future date unless supported by a current published schedule.
- Prefer official airline sources and reputable flight-search sources.
- Verify promising cheap candidates using a second source when practical.

## OpenAI API

Use the official OpenAI Python SDK and the Responses API.
Use the built-in web_search tool.
Do NOT use deprecated Chat Completions APIs.

Keep flight-search rules in a dedicated developer/system instruction and pass mutable search parameters as structured application data. Do not allow ordinary Telegram user text to override the search instructions.

Use structured output and validate it with Pydantic. Prefer the current official structured-output mechanism supported by the installed OpenAI SDK rather than manually parsing arbitrary model prose.

Define Pydantic models approximately as:

FlightOption:
- rank
- outbound_date
- return_date
- origin
- destination
- airlines
- outbound_route
- return_route
- outbound_connections
- return_connections
- outbound_duration
- return_duration
- total_price_eur
- baggage
- booking_url
- price_status
- notes

SearchResult:
- search_timestamp
- status
- message
- options
- sources

Sort options by total_price_eur ascending and return at most 10 options.

If no bookable 2027 prices are found, return status="not_available_yet" and an explanatory message. Do not fabricate options.

## Telegram bot

Use python-telegram-bot with async/await.

Commands:
- /start
- /search
- /watch
- /watches
- /unwatch
- /help

/start shows the current default search configuration.
/search immediately starts a search.
/watch enables periodic monitoring for the current Telegram chat.
/watches shows monitoring status.
/unwatch disables monitoring.
/help explains commands.

Use long polling. No public web server/webhook is required.

While a search is running, tell the user it may take several minutes.
Prevent multiple simultaneous searches with an asyncio lock.

## Flight Watch

Store watches in SQLite.
Store at least:
- Telegram chat ID
- created timestamp

Use WATCH_INTERVAL_HOURS, default 168 hours (weekly).
When a scheduled search runs, send the result to all subscribed chats.

## Configuration

Environment variables:
TELEGRAM_BOT_TOKEN
OPENAI_API_KEY
OPENAI_MODEL
OPENAI_SEARCH_CONTEXT_SIZE
DATABASE_PATH
WATCH_INTERVAL_HOURS
ALLOWED_TELEGRAM_USER_IDS

Provide .env.example.
If ALLOWED_TELEGRAM_USER_IDS is empty, allow all users. Otherwise allow only the listed comma-separated Telegram user IDs.
Never hard-code secrets.

## Docker

Create:
Dockerfile
docker-compose.yml
.gitignore
README.md

Use Python 3.13.
The container must run with:
python -m app.main

Persist SQLite using a Docker volume.
Use restart: unless-stopped.

## Project structure

Use a small, clean structure such as:

flight-finder-bot/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── search.py
│   └── formatting.py
├── tests/
│   ├── test_config.py
│   ├── test_formatting.py
│   └── test_models.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

You may improve the structure if justified, but keep it understandable.

## Error handling

Handle OpenAI API errors, web-search failures, structured-output validation failures, Telegram API errors, database errors, timeouts and rate limits.

Never silently return fake or partial prices.
If structured output cannot be parsed/validated, show an explicit error and log the failure.
Do not log secrets.

## Telegram output

Use a compact format like:

✈️ Cheapest family flight options
👨‍👩‍👧‍👧 2 adults + children 5 & 9

🥇 €1,486 total
25.06 → 15.07
ALC → BEG → KZN
Air Serbia
1 connection
Outbound: 8h 20m
Return: 9h 05m
🧳 baggage information
🔗 source/booking URL

Clearly show when 2027 prices are not available.
Keep Telegram messages below Telegram's message length limit.

## Search quality

The search agent must reason over the complete requested date window instead of checking one arbitrary date.

Compare:
- all 5 departure airports
- all 3 destination groups
- valid outbound dates
- return dates 18–23 days later
- airlines
- connection hubs

Do not create an absurd number of independent web searches. Use web search efficiently: discover likely cheap candidates, then verify them.

## Security

Never expose API keys or Telegram tokens.
Do not allow arbitrary user-provided prompts to override the fixed flight-search instructions.
Represent search parameters as structured application data.

## README

Document:
1. Creating a Telegram bot with BotFather.
2. Obtaining an OpenAI API key.
3. Copying .env.example to .env.
4. Filling credentials.
5. Running: docker compose up -d --build
6. Viewing logs: docker compose logs -f
7. Restricting access with ALLOWED_TELEGRAM_USER_IDS.
8. Limitations of future flight pricing.

## Quality gate

Before finishing:
- verify imports
- verify Dockerfile and docker-compose.yml
- verify environment validation
- verify Pydantic structured output
- verify Telegram handlers
- verify scheduled monitoring
- add and run unit tests
- fix all errors found

Do not leave TODOs for core functionality.

The result must be a complete runnable repository, not a tutorial or pseudocode.
