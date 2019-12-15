ROOT_DIR = $(CURDIR)
SOURCE_DIR = $(CURDIR)/back

MANAGER = python $(SOURCE_DIR)/manage.py
VENV = . $(ROOT_DIR)/.venv/bin/activate;
SUPERVISOR = sudo supervisorctl

.PHONY : static
static:
	$(VENV) $(MANAGER) collectstatic --noinput

.PHONY : pip
pip:
	$(VENV) pip install --exists-action s -r $(ROOT_DIR)/requirements.txt

.PHONY : migrate
migrate:
	$(VENV) $(MANAGER) migrate --noinput

.PHONY : makemigrations
makemigrations:
	$(VENV) $(MANAGER) makemigrations --noinput

.PHONY : runserver
runserver:
	$(VENV) $(MANAGER) runserver 127.0.0.1:8120

.PHONY : reload
reload:
	cd $(ROOT_DIR) ; touch reload

# Update instance
.PHONY : update
update: pip migrate static reload
