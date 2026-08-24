Perform a final production-readiness review of the repository.

Check:
- no secrets committed
- .env is ignored
- API keys are never logged
- Telegram access restriction works
- arbitrary Telegram text cannot override the fixed search instructions
- OpenAI errors are handled safely
- rate limits/timeouts are handled
- malformed model output cannot crash the bot permanently
- scheduled watch failures do not stop the bot
- SQLite is persisted correctly in Docker
- Docker restart policy is correct
- tests cover the critical paths

Run the full test suite and fix all remaining issues.

Do not add unnecessary infrastructure. Keep the application small enough to run comfortably on a small VPS.
