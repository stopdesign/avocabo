import re
from time import sleep

import nltk
import logging
import json

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand
from collections import Counter

from main.models import Word, Definition, Example, Pronunciation, List, Sentence

logger = logging.getLogger(__name__)

M_ = '\033[1;35;48m'
_M = '\033[0m'

B_ = '\033[1;37;40m'
_B = '\033[0m'

D_ = '\033[1;32;40m'
_D = '\033[0m'


def clean(word):
    word = word.lower()
    word = word.strip(',').strip('.').strip(';').strip('!').strip('?').strip('-').strip()
    return word


def replace_spaces(match):
    return '[' + match.group(1).replace(' ', ' ') + '](' + match.group(2).replace(' ', ' ') + ')'


def sentence_converter(s):
    return re.sub(r'\[(.*?)\]\s*\((.*?)\)', replace_spaces, s)


class Command(BaseCommand):
    def_list = None

    def handle(self, *args, **options):

        self.def_list = List.objects.get(id=20)

        Sentence.objects.all().delete()

        # self.test('prepositions-adjectives.txt', 'adjective_and_preposition')
        # self.test('prepositions-nouns.txt', 'noun_and_preposition')  # 18
        self.test('01_part.txt')  # 19

    def test(self, filename):

        f = open(filename, 'r')

        for line in f.readlines():
            text = line.strip()

            # print('1', text)
            # точка в конце предложения
            text = re.sub(r'(?P<txt>[\w])$', '\g<txt>.', text)
            # отбитая пунктуация
            text = re.sub(r'(?P<pre>[\s ]+)(?P<txt>[!?.,;])', '\g<txt>', text)
            # пробел после скобки
            text = re.sub(r'(?P<pre>[)\]])(?P<txt>\w)', '\g<pre> \g<pre>', text)
            # побить диалоги
            text = re.sub(r'(?P<pre>[!?.,;])\s+(?P<txt>[\-—–]\s+)', '\g<pre> \n— ', text)
            # lower case в скобках
            text = re.sub(r'\((.*?)\)', lambda s: '(' + s.group(1).lower().strip() + ')', text)
            # неразрывные проблелы после 1-2 символов
            text = re.sub(r'(?P<pre> [-\w]{1,2}) (?P<txt>[a-zA-Z])', '\g<pre> \g<txt>', text)
            text = text.replace(')', ') ').replace('  ', ' ')
            # print('2', text)

            if '\n— ' in text:
                text = '— ' + text

            # обработка разметки
            text = sentence_converter(text)

            print(text)
            print()

            s = Sentence(
                text=text,
            )
            s.save()
            self.def_list.sentences.add(s)
