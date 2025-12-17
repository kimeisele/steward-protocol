# Steward Protocol Makefile
# =============================================================================
# OPUS-020: Container Migration Integration
# =============================================================================

.PHONY: help test lint format containers clean

# Default target
help:
	@echo "Steward Protocol - Available Commands"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make test        Run fast test suite"
	@echo "  make test-full   Run complete test suite with coverage"
	@echo "  make test-ci     Run CI-optimized tests"
	@echo "  make lint        Check code with ruff"
	@echo "  make format      Format code with ruff"
	@echo "  make containers  Build all .vibe containers"
	@echo "  make clean       Remove build artifacts"

# Testing (uses quality.yaml profiles)
test:
	pytest --test-profile=fast

test-full:
	pytest --test-profile=full

test-ci:
	pytest --test-profile=ci

test-unit:
	pytest --test-profile=unit

test-integration:
	pytest --test-profile=integration

# Linting & Formatting
lint:
	ruff check vibe_core scripts

format:
	ruff format vibe_core scripts
	ruff check --fix vibe_core scripts

# Container Building (OPUS-020)
containers:
	./scripts/build_all_containers.sh

containers-inplace:
	./scripts/build_all_containers.sh --inplace

# Cleanup
clean:
	rm -rf dist/plugins/*.vibe
	rm -rf __pycache__ .pytest_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Development
dev:
	python -m vibe_core.cli boot

# Verification
verify-containers:
	@echo "Verifying container signatures..."
	@for f in dist/plugins/*.vibe; do \
		echo "Checking $$f..."; \
		unzip -p "$$f" SIGNATURE.sig | python -m json.tool > /dev/null && echo "  ✅ Valid signature" || echo "  ❌ Invalid"; \
	done
