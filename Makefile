# Kingsman Jiu Jitsu Studio — static one-page site (no build).
# Makefile is a thin dispatcher over plain shell commands (this repo has
# no package.json). Serve, refresh photos from the scraped IG JSON, verify.

SHELL := /bin/bash
PORT  ?= 8091
BASE  ?= http://127.0.0.1:$(PORT)
PY    ?= python3

.DEFAULT_GOAL := help

.PHONY: help serve photos pages check assets verify doctor

help: ## Show this help
	@printf 'Kingsman Jiu Jitsu Studio — static one-page site.\n\nTargets:\n\n'
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  %-10s %s\n", $$1, $$2}' | sort

serve: ## Serve the site locally (default http://127.0.0.1:8091; Ctrl-C to stop)
	bunx http-server . -p $(PORT) -c-1

photos: ## (Re)download Instagram photos from the scraped profile JSON into assets/
	$(PY) scripts/download_instagram_photos.py $$(ls dataset_instagram-profile-scraper_*.json 2>/dev/null | head -1)

pages: ## Regenerate the individual class pages (pages/clases/*.html)
	$(PY) scripts/build_pages.py

check: assets ## Verify the served site: assets 200, internal links, JSON-LD validity
	$(PY) scripts/check.py $(BASE)

assets: ## Verify asset provenance: nada de Chile puede ser material de Guayaquil
	$(PY) scripts/check_assets.py

verify: check ## Run `make serve` first, then verify the live site

doctor: ## Check prerequisite tools (python3 + bun, or python3 + node/npx)
	@command -v $(PY) >/dev/null 2>&1 || { echo "error: python3 not found"; exit 1; }
	@echo "python3: OK"
	@if command -v bun >/dev/null 2>&1; then echo "bun: OK"; \
	elif command -v npx >/dev/null 2>&1; then echo "npx: OK"; \
	else echo "error: need 'bun' or 'node/npx' to serve via http-server"; exit 1; fi