# coding: utf-8
#
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(BASE_DIR)

ENV_NAME = "dev"

DEBUG = True

# с http, без слеша
HOST = "https://dev.stopdesign.ru"

INTERNAL_IPS = []

ALLOWED_HOSTS = [
    "0.0.0.0",
    "127.0.0.1",
]

SECRET_KEY = "4as3flh1vjaksLknKHijd1i5mnU3dhlfkhgsalkdvagO<m3ljsFfnfkvj2akj1dd"

AUTH_PASSWORD_VALIDATORS = []

SESSION_COOKIE_SECURE = False

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
