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

.PHONY : front
front:
	cd $(ROOT_DIR)/front ; npm install ; NODE_ENV="production" npm run build

.PHONY : frontcopy
frontcopy:
	cp -r $(ROOT_DIR)/front/public $(ROOT_DIR)/www/

.PHONY : reload
reload:
	cd $(ROOT_DIR) ; sudo supervisorctl restart all
#	cd $(ROOT_DIR) ; touch reload

# Update instance
.PHONY : update
update: front pip migrate static frontcopy reload
