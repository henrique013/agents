.PHONY: setup tests

PYTHON := python3
NODE := node
NPM := npm

setup:
	@command -v $(PYTHON) > /dev/null || { echo "Erro: python3 não encontrado. Instale Python >=3.10 e rode make setup novamente." >&2; exit 1; }
	@$(PYTHON) -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' || { echo "Erro: Python >=3.10 é obrigatório; encontrado $$($(PYTHON) --version 2> /dev/null || echo indisponível)." >&2; exit 1; }
	$(PYTHON) --version
	@command -v $(NODE) > /dev/null || { echo "Erro: node não encontrado. Instale Node >=22 e rode make setup novamente." >&2; exit 1; }
	@node_major="$$( $(NODE) -p 'Number(process.versions.node.split(".")[0])' 2> /dev/null )"; \
		if [ -z "$$node_major" ] || [ "$$node_major" -lt 22 ] 2> /dev/null; then \
			echo "Erro: Node >=22 é obrigatório; encontrado $$($(NODE) --version 2> /dev/null || echo indisponível)." >&2; \
			exit 1; \
		fi
	$(NODE) --version
	@command -v $(NPM) > /dev/null || { echo "Erro: npm não encontrado. Instale npm e rode make setup novamente." >&2; exit 1; }
	$(NPM) --version
	$(NPM) ci
	LEFTHOOK=1 $(NPM) run --silent lefthook:install

tests:
	$(PYTHON) -B -m unittest discover -s tests -v
