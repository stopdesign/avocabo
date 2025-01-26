from collections import OrderedDict
from decimal import Decimal

"""
https://django-constance.readthedocs.io/

The supported types:
bool, int, float, Decimal, str, datetime, date, time

Command Line:
./manage.py constance list
./manage.py constance get THE_ANSWER
./manage.py constance set SITE_NAME "Another Title"

Code usage:
from constance import config
config.THE_ANSWER

"""

CONSTANCE_SUPERUSER_ONLY = True

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
# CONSTANCE_DATABASE_CACHE_BACKEND = 'constance'
# CONSTANCE_DATABASE_CACHE_AUTOFILL_TIMEOUT = 3600 * 24


CONSTANCE_ADDITIONAL_FIELDS = {
    "waves_address": [
        "django.forms.fields.CharField",
        {
            "widget": "django.forms.TextInput",
            "max_length": 100,
            "validators": [],
            "required": False,
        },
    ],
    "ethereum_address": [
        "django.forms.fields.CharField",
        {
            "widget": "django.forms.TextInput",
            "max_length": 100,
            "validators": [],
            "required": False,
        },
    ],
    "input_field": [
        "django.forms.fields.CharField",
        {
            "widget": "django.forms.TextInput",
            "max_length": 100,
            "validators": [],
            "required": False,
        },
    ],
    "url_field": [
        "django.forms.fields.URLField",
        {
            "widget": "django.forms.TextInput",
            "max_length": 100,
            "validators": [],
            "required": False,
        },
    ],
    "email_field": [
        "django.forms.fields.EmailField",
        {
            "widget": "django.forms.TextInput",
            "max_length": 100,
            "validators": [],
            "required": False,
        },
    ],
}

CONSTANCE_CONFIG = OrderedDict(
    [
        ("ETHEREUM_CONFIRMATION_WALLET", ("", "", "ethereum_address")),
        ("WAVES_CONFIRMATION_WALLET", ("", "", "waves_address")),
    ]
)


# CONSTANCE_CONFIG_FIELDSETS must contain all fields from CONSTANCE_CONFIG

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    [
        ("Ethereum", ("ETHEREUM_CONFIRMATION_WALLET",)),
        ("Waves", ("WAVES_CONFIRMATION_WALLET",)),
    ]
)
