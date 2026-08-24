# Copilot prompts for Flight Finder Bot

Use these prompts in GitHub Copilot Agent mode in order:

1. `01_build_project.md` — create the complete repository.
2. `02_review_openai.md` — audit/fix OpenAI Responses API + web search integration.
3. `03_test_search_quality.md` — audit the flight-search logic and prompt.
4. `04_final_security_review.md` — final production/security review.

Important: ask Copilot to use the current official OpenAI documentation when reviewing API usage. Keep `OPENAI_MODEL` configurable instead of hard-coding a model name.
