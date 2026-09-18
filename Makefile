# Convenience wrappers around the bench CLI and catalog generator.
# `bench` is the primary interface; these are shortcuts.

.PHONY: help catalog check validate doctor list ports status down-all new proxy proxy-down audit

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	 | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

catalog:         ## Regenerate catalog/benchmarks.yaml and docs/CATALOG.md
	python3 tools/catalog.py

check:           ## Fail if the catalog / CATALOG.md are out of date (CI)
	python3 tools/catalog.py --check

doctor:          ## Environment + catalog sanity check
	./bench doctor

list:            ## List hostable targets and their ports
	./bench list

ports:           ## Print the full host port map
	./bench ports

status:          ## Show running bench targets
	./bench status

down-all:        ## Stop and remove everything bench started
	./bench down --all

validate:        ## Validate manifests + catalog sync (CI)
	./bench validate

new:             ## Scaffold a new target: make new DOMAIN=web
	./bench new $(DOMAIN) $(if $(TEMPLATE),--template $(TEMPLATE),)

proxy:           ## Start the nginx reverse proxy for running targets
	./bench proxy up

proxy-down:      ## Stop the nginx reverse proxy
	./bench proxy down

audit:           ## Regenerate the corpus audit (docs/AUDIT.md)
	./bench audit
