BASE_DIR = $(CURDIR)

MANAGE = python $(BASE_DIR)/back/manage.py
VENV = . $(BASE_DIR)/.venv/bin/activate; \

FMT = printf "\033[34m%-20s\033[0m %s\n"
RGX = /^[0-9a-zA-Z_-]+:.*?\#/

help :: # Show this message
	@awk '{FS=": #"} $(RGX) {$(FMT),$$1,$$2}' $(MAKEFILE_LIST)

clean: # Clean project
	find . -name "*.pyc" -delete
	find . -name "*.orig" -delete

pip: # Install python dependencies
	$(VENV) pip install -r $(BASE_DIR)/requirements.txt \
	--upgrade --no-python-version-warning

static: # Django: collectstatic
	$(VENV) $(MANAGE) collectstatic --noinput

migrate: # Django: migrate
	$(VENV) $(MANAGE) migrate --noinput

test: # Django: test
	$(VENV) $(MANAGE) test --noinput

run: # Django: runserver at 127.0.0.1:8800
	$(VENV) $(MANAGE) runserver 127.0.0.1:8120

run0: # Django: runserver at 0.0.0.0:8800
	$(VENV) $(MANAGE) runserver 0.0.0.0:8120

touch_reload: # Reload instance
	cd $(BASE_DIR) && touch reload

update: # Run multiple targets
	make pip migrate static
	service bookest_dev_django restart

count: # Count code lines with cloc
	cloc --vcs git \
		--exclude-dir=migrations,libs,plugins \
		--exclude-lang=SVG,JSON,YAML,Text,make,Markdown,TOML,INI,"PO File" \
		--not-match-f='min.js|min.css|bootstrap|icons.css' \
		--quiet

# deploy: # Deploy via ssh
# 	$(SSH) "cd $(SERVER_PATH) && git reset --hard HEAD"
# 	@echo ""
# 	$(SSH) "cd $(SERVER_PATH) && git pull -f --quiet"
# 	@echo ""
# 	$(SSH) "cd $(SERVER_PATH) && make update"
