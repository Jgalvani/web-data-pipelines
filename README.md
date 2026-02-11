# Web Data Pipelines

A Playwright + Python automation framework for browser-driven data collection across public web portals.

## Features

- **Page Object Model (POM)** architecture with YAML-driven selectors
- **Anti-detection**: fingerprint rotation, stealth patches, human-like delays, rate limiting
- **Pagination** handling with configurable strategies
- **Session management** with automatic timeout detection and refresh
- **Multi-portal support** — add new portals via YAML config + Python modules
- **Export** to JSON files or HTTP API endpoints (with retries)
- **Daily scheduling** via APScheduler cron jobs
- **Concurrent multi-portal** — run all portals in parallel with `run-all`
- **Fully async** throughout (Playwright async API, httpx)

## Quick Start

```bash
# Install dependencies
pipenv shell
pipenv install --dev
pipenv run playwright install chromium

# Run the demo portal (headless)
pipenv run python main.py run books_toscrape --max-pages 2

# Run with visible browser
pipenv run python main.py run books_toscrape --no-headless --max-pages 2

# List available portals
pipenv run python main.py list-portals

# Register a scheduled job (non-blocking, saves to DB)
pipenv run python main.py schedule books_toscrape --cron "0 6 * * *"

# List / update / remove scheduled jobs
pipenv run python main.py list-jobs
pipenv run python main.py update-job books_toscrape_cron "30 8 * * *"
pipenv run python main.py remove-job books_toscrape_cron

# Run all registered portals concurrently
pipenv run python main.py run-all --max-pages 2

# Start the scheduler (blocking, runs all registered jobs)
pipenv run python main.py start-scheduler
```

## Configuration

Copy `.env.example` to `.env` and adjust values:

```bash
cp .env.example .env
```

Portal-specific settings live in `config/portals/<portal_name>.yaml`.

## Project Structure

```
web_data_pipelines/
├── main.py                       # CLI entry point (click)
├── config/                       # Settings, logging, portal YAML configs
├── core/
│   ├── browser/                  # Browser lifecycle, fingerprints, proxy
│   ├── anti_detection/           # Stealth, delays, rate limiter, sessions
│   ├── pages/                    # Base Page Object Model
│   ├── pipelines/                # Base pipeline (template method)
│   ├── models/                   # Pydantic base models
│   ├── export/                   # JSON and API exporters
│   └── utils/                    # Retry, date utilities
├── portals/
│   └── books_toscrape/           # Demo portal implementation
├── scheduling/                   # APScheduler integration
├── tests/                        # Unit and integration tests
└── output/                       # Collected data (gitignored)
```

## Adding a New Portal

1. Copy `config/portals/_template.yaml` → `config/portals/my_portal.yaml`
2. Create `portals/my_portal/` with:
   - `pages/` — Page Object classes extending `BasePage`
   - `models.py` — Pydantic data models extending `BaseDataModel`
   - `pipeline.py` — Pipeline class extending `BasePipeline`
3. Register in `main.py` → `PORTAL_REGISTRY`

## Testing

```bash
# Unit tests
pipenv run pytest tests/unit/ -v

# Integration tests (requires network)
pipenv run pytest tests/integration/ -v

# All tests
pipenv run pytest -v
```

## Docker

### How it works

The `Dockerfile` builds a self-contained image with Python 3.13, all dependencies, and the Chromium browser pre-installed. The image uses `main.py` as its entrypoint, so any CLI command can be passed as arguments.

The `docker-compose.yml` defines two services:
- **`run`** — one-shot data collection, exits when done. Output is mounted to `./output/` on the host.
- **`scheduler`** — long-running process that executes registered cron jobs. Restarts automatically.

### Build the image

```bash
docker build -t web-data-pipelines .
```

### Run a one-shot collection

```bash
# Using docker directly
docker run --rm -v $(pwd)/output:/app/output web-data-pipelines \
    run books_toscrape --max-pages 2

# Run all portals concurrently
docker run --rm -v $(pwd)/output:/app/output web-data-pipelines \
    run-all --max-pages 2

# Using docker-compose
docker compose run --rm run
```

### Manage scheduled jobs

```bash
# Register a job
docker run --rm -v $(pwd)/output:/app/output web-data-pipelines \
    schedule books_toscrape --cron "0 6 * * *"

# List registered jobs
docker run --rm -v $(pwd)/output:/app/output web-data-pipelines list-jobs

# Update a job's cron expression
docker run --rm -v $(pwd)/output:/app/output web-data-pipelines \
    update-job books_toscrape_cron "30 8 * * *"

# Remove a job
docker run --rm -v $(pwd)/output:/app/output web-data-pipelines \
    remove-job books_toscrape_cron
```

### Run the scheduler (long-running)

```bash
# Using docker-compose (recommended — auto-restarts)
docker compose up -d scheduler

# Check logs
docker compose logs -f scheduler

# Stop
docker compose down
```

The `output/` volume is shared between all commands so the scheduler database and JSON exports persist on the host.

### Environment variables

Pass configuration via `.env` file (used by docker-compose) or `-e` flags:

```bash
docker run --rm -e HEADLESS=true -e LOG_LEVEL=DEBUG \
    -v $(pwd)/output:/app/output web-data-pipelines \
    run books_toscrape --max-pages 1
```

## Dependencies

**Runtime**: playwright, playwright-stealth, pydantic, pydantic-settings, pyyaml, httpx, tenacity, apscheduler, structlog, python-dotenv, rich, click, sqlalchemy

**Dev**: pytest, pytest-asyncio, pytest-playwright, ruff
