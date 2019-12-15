import re

import nltk
import logging
import json

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand
from collections import Counter

from main.models import Word, Definition, Example, Pronunciation, List

logger = logging.getLogger(__name__)

M_ = '\033[1;35;48m'
_M = '\033[0m'

B_ = '\033[1;37;40m'
_B = '\033[0m'

D_ = '\033[1;32;40m'
_D = '\033[0m'


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


def sub_index(a, b):
    """
    Поиск индекса первого вхождения массива в другой массив.
    """
    a = list(a)
    b = list(b)
    len_b = len(b)
    for i in range(len(a)):
        if a[i:i+len_b] == b:
            return i


def clean(word):
    word = word.lower()
    word = word.strip(',').strip('.').strip(';').strip('!').strip('?').strip('-').strip()
    return word


class Command(BaseCommand):
    def_list = None

    def handle(self, *args, **options):

        self.def_list = List.objects.get(id=16)

        # self.test('hp.txt')
        # self.test('mart.txt')
        # self.test('full.txt')
        self.test('verb_prepositions.txt')

    def load_yandex_data(self, spelling, pos):

        ya_base = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=%s&lang=en-en&text=%s'
        url = ya_base % (settings.YANDEX_DICT_API_KEY, spelling)
        r = requests.get(url)

        res = r.json()
        # print(json.dumps(res, indent=2, ensure_ascii=False))

        try:
            definitions = res['def'][0]['tr']
        except:
            definitions = []

        means = []
        syns = []

        print(definitions)

        for definition in definitions:
            # if 'pos' not in definition:
            #     continue
            #
            # if definition['pos'] != pos:
            #     continue

            text = definition.get('text')
            syn = definition.get('syn', [])

            for s in syn:
                if spelling not in s['text']:
                    syns.append(s['text'])

            if spelling in text:
                continue

            means.append(text)

        return means[:5], syns[:5]

    def parse(self, text, rx):
        match = re.search(rx, text)
        if match:
            return match.group(1)
        else:
            return ''

    def load_cambrige(self, word, url_spelling, item):

        url = 'https://dictionary.cambridge.org/dictionary/english-russian/%s' % url_spelling

        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            return

        soup = BeautifulSoup(r.text, 'html.parser')

        spelling = self.parse(r.text, r'<div class="h3 di-title cdo-section-title-hw">([^<]*?)</div>')
        pos = self.parse(r.text, r'><span class="pos">([^<]*?)</span>')
        page_id = requests.utils.urlparse(r.url).path.split('/')[-1]

        entry_body = soup.find('div', {'class': 'normal-entry-body'})

        has_res = False

        if entry_body:
            title = ''

            for sense_block in entry_body.select('.sense-block') or []:
                notes = []

                s = sense_block.select('.sense-head > .sense-title')
                if s:
                    title = s[0].get_text(strip=True, separator=' ')

                xref = ''
                s = sense_block.select('.sense-body .epp-xref')
                if s:
                    xref = s[0].get_text(strip=True)

                phrase_title = None
                s = sense_block.select('.sense-body .phrase-title')
                if s:
                    phrase_title = s[0].get_text(strip=True)

                phrase_info = None
                s = sense_block.select('.sense-body .phrase-info')
                if s:
                    phrase_info = s[0].get_text(strip=True)
                    notes.append(phrase_info)

                translation = None
                s = sense_block.select('.sense-body .trans')
                if s:
                    translation = s[0].get_text(strip=True, separator=' ')

                interpretation = None
                s = sense_block.select('.sense-body .def')
                if s:
                    interpretation = s[0].get_text()

                examp = []
                s = sense_block.select('.sense-body .examp')
                for e in s:
                    ex = e.find('span', {'class': 'eg'}).get_text(strip=True, separator=' ').strip('.').strip()
                    ex = ex.replace(' ,', ',').replace(' .', '.')

                    found_all_parts = True
                    # должны быть совпадения всех предлогов/союзов (основное слово и так есть)
                    for part in item.split(' ')[1:]:
                        if (' %s ' % part) not in (' %s ' % ex.replace(',', ' ').replace('.', ' ').replace('?', ' ').replace('!', ' ')):
                            found_all_parts = False

                    if found_all_parts:
                        examp.append({
                            'text': ex,
                        })

                if examp:
                    has_res = True
                    print(title)
                    print(xref)
                    print(translation)
                    print(interpretation)
                    print(json.dumps(examp, indent=2))
                    print()

                    if phrase_title:
                        spelling_final = phrase_title
                    else:
                        spelling_final = spelling

                    definition_obj = Definition(
                        word=word,
                        spelling=spelling_final,
                        interpretation=interpretation,
                        translation=translation,
                        context=title.capitalize(),
                        level=xref,
                        note=('; '.join(notes)).strip('; ')
                    )
                    definition_obj.save()

                    for example in examp:
                        example_obj = Example(
                            definition=definition_obj,
                            text=example['text'],
                        )
                        example_obj.save()

        return has_res

    def test(self, filename):

        f = open(filename, 'r')

        for line in f.readlines():
            line = line.strip()

            item, examples = line.split(' — ')
            item = item.strip()

            ws = Word.objects.filter(spelling__iexact=item).count()
            ds = Definition.objects.filter(spelling__iexact=item).count()

            # means, syns = self.load_yandex_data(item, 'phrase')
            # means_str = ('; '.join(means)).strip().strip(';')
            # syns_str = ('; '.join(syns)).strip().strip(';')

            if ds or ws:
                logging.debug(item + ': ')
            else:
                logging.warning(item + ': ')

            first_word = item.split(' ')[0]

            spelling = clean(item)

            pos = 'word_plus_preposition'

            # удаление экземпляров этого слова, которые уже есть в списке
            for same_word in Word.objects.filter(spelling__iexact=spelling, part_of_speech__iexact=pos):
                self.def_list.words.remove(same_word)
                if same_word.list.count() == 0:
                    same_word.delete()

            # добавляю слово в список
            word = Word(
                spelling=spelling,
                part_of_speech=pos,
                transcription='',
                short_mean='',
                syn_string='',
            )
            if ds or ws:
                word.is_hidden = True
            word.save()
            self.def_list.words.add(word)

            has_res = self.load_cambrige(word, item, item)

            if not has_res:
                has_res = self.load_cambrige(word, first_word, item)

            if not has_res:

                definition_obj = Definition(
                    word=word,
                    spelling=spelling,
                    interpretation='???',
                    translation='???',
                    context='',
                    level='',
                    note=''
                )
                definition_obj.save()

                for example in examples.split('/'):
                    example = example.strip()
                    example_obj = Example(
                        definition=definition_obj,
                        text=example,
                    )
                    example_obj.save()

                print()
                logging.error(item)
                print()
