Review the entire flight-finder Telegram bot as a senior Python/OpenAI engineer.

Focus especially on the OpenAI Responses API and built-in web_search implementation.

Use the CURRENT official OpenAI API/SDK documentation and correct the project if necessary.

Check and fix:
- deprecated API usage
- incorrect Responses API calls
- incorrect web_search tool configuration
- unsupported parameters
- incorrect async usage
- incorrect model configuration
- incorrect structured-output implementation
- incorrect Pydantic integration
- incorrect response parsing
- incorrect handling of web-search sources/citations
- SDK version compatibility

Do not assume that an older Chat Completions example is valid for Responses API.
Do not invent API parameters.

Also verify:
- Telegram handlers
- asyncio locking
- APScheduler/job queue usage
- SQLite handling
- Docker configuration
- environment validation
- tests
- Telegram message length handling
- error handling and rate-limit handling

Run the tests and fix all failures.

Do not rewrite working parts unnecessarily.
Do not change the flight-search requirements unless required for correctness.
