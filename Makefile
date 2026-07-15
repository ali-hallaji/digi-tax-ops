# DigiTax ops — founder convenience targets. Run from digi-tax-ops/.
# `make help` lists targets.

.PHONY: help reset-world

help: ## List available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

reset-world: ## Wipe + reseed the 12-persona verification world, regen docs, print the login table
	@bash scripts/reset_world.sh
