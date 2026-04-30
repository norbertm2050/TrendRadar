# Repository Guidelines

## Project Structure & Module Organization

TrendRadar is a Python 3.12 news aggregation and analysis tool. Core application code lives in `trendradar/`: `core/` handles configuration and scheduling, `crawler/` fetches sources, `ai/` formats and calls AI services, `storage/` manages local/remote persistence, `notification/` sends messages, and `report/` builds HTML/RSS output. MCP server code is under `mcp_server/`, with tools in `mcp_server/tools/` and shared services in `mcp_server/services/`. Runtime configuration and prompt templates live in `config/`; generated data and reports belong in `output/`. Docker assets are in `docker/`, static docs in `docs/`, and public images in `_image/`.

## Build, Test, and Development Commands

- `uv sync` installs the locked Python environment from `pyproject.toml` and `uv.lock`.
- `uv run python -m trendradar` runs one local crawl/analyze/report cycle.
- `uv run trendradar-mcp` starts the MCP server using the packaged console script.
- `./start-http.sh` starts the MCP HTTP server on `0.0.0.0:3333`.
- `cd docker && docker compose up -d` starts the published `trendradar` and optional `trendradar-mcp` services.
- `cd docker && docker compose -f docker-compose-build.yml build` builds local images for Docker verification.
- `uv run python -m compileall trendradar mcp_server` is the current lightweight syntax check.

## Coding Style & Naming Conventions

Use 4-space indentation, type hints where they clarify public interfaces, and UTF-8 for existing Chinese user-facing text. Keep modules focused by domain and prefer existing helpers before adding new utilities. Use `snake_case` for functions, variables, files, and config keys; use `PascalCase` for classes. Preserve existing console/log wording style when editing operational output.

## Testing Guidelines

Focused unit tests live under `tests/` and use Python `unittest`; name files like `test_report_dedupe.py` or `test_mcp_tools.py`. Run `uv run python -m unittest discover -s tests` before shipping behavior changes. Always run `uv run python -m compileall trendradar mcp_server`; for crawler, notification, AI, or Docker changes, also run the relevant local command or container smoke test and record any skipped external-service checks.

## Commit & Pull Request Guidelines

Git history uses Conventional Commit-style summaries, often with scopes, for example `fix(core): ...`, `feat(ci): ...`, and `refactor(docker): ...`. Keep commits narrow and explain user-visible impact. Pull requests should include a concise description, linked issue when applicable, verification commands, config/env changes, and screenshots for HTML/report or docs UI changes. Do not commit secrets, generated local databases, or private notification endpoints.
