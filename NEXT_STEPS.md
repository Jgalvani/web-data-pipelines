# Next Steps

## Short-term Enhancements

- [ ] Add CSV exporter alongside JSON
- [ ] Add database exporter (SQLite/PostgreSQL via SQLAlchemy)
- [ ] Implement `infinite_scroll` and `page_number` pagination strategies
- [ ] Add date-range input support for portals that filter by date
- [ ] Improve error recovery: retry individual page extractions on failure
- [ ] Add progress bar (rich) during collection

## Anti-Detection

- [ ] Add CAPTCHA detection and notification (webhook/email alert)
- [ ] Implement cookie persistence across sessions
- [ ] Add more fingerprint profiles and rotate viewport sizes
- [ ] Implement mouse movement simulation for enhanced stealth

## Infrastructure

- [x] Docker containerization with Playwright pre-installed
- [x] Concurrent multi-portal execution (`run-all` command)
- [x] Scheduler job management (list, update, remove via CLI)
- [ ] CI/CD pipeline (GitHub Actions) running lint + unit tests
- [ ] Monitoring dashboard for scheduled runs (Grafana/Prometheus)
- [ ] Webhook notifications on pipeline failures (Slack, email)

## New Portals

- [ ] Add 2-3 additional demo portals to prove multi-portal architecture
- [ ] Create a portal generator CLI command (`main.py new-portal <name>`)

## Testing

- [ ] Add snapshot tests for page object extraction
- [ ] Add performance benchmarks for rate limiter
- [ ] Mock-based unit tests for pipeline orchestration
- [ ] Add load testing for API exporter
