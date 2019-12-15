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

from main.models import Word, Definition, Example, Pronunciation, List

logger = logging.getLogger(__name__)

M_ = '\033[1;35;48m'
_M = '\033[0m'

B_ = '\033[1;37;40m'
_B = '\033[0m'

D_ = '\033[1;32;40m'
_D = '\033[0m'

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,ms;q=0.8,te;q=0.7',
    'Cache-Control': 'max-age=0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://7esl.com',
    'Referer': 'https://7esl.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
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

        self.def_list = List.objects.get(id=19)

        # self.test('prepositions-adjectives.txt', 'adjective_and_preposition')
        # self.test('prepositions-nouns.txt', 'noun_and_preposition')  # 18
        self.test('prepositions-verbs.txt', 'verb_and_preposition')  # 19

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

    def test(self, filename, pos):

        f = open(filename, 'r')

        for link in f.readlines():
            link = link.strip()

            sleep(1)

            print('\n\n', link)

            r = requests.get(link, headers=headers)

            if r.status_code != 200:
                logging.error('status %s' % r.status_code)

            all_text = r.text.split('</ul><h3><span class="ez-toc-section"')[1]
            all_text = all_text.split('</h3>')[1]
            all_text = all_text.split('<h2>')[0]

            soup = BeautifulSoup(all_text, 'html.parser')

            # entry_body = soup.find('div', {'class': 'normal-entry-body'})
            # idiom_body = soup.find('div', {'class': 'idiom-body'})

            item = soup.select('p > strong')
            for el in item:
                spelling = el.get_text(strip=True)
                siblings = el.parent.find_next_siblings('ul')
                example = siblings[0].get_text(strip=False)

                example = example.replace('  ', ' ').replace('  ', ' ').strip()
                spelling = clean(spelling)

                print(spelling, example)

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
                word.save()
                self.def_list.words.add(word)

                definition_obj = Definition(
                    word=word,
                    spelling=spelling,
                    interpretation='',
                    translation='',
                    context='',
                    level='',
                    note='',
                )
                definition_obj.save()

                example_obj = Example(
                    definition=definition_obj,
                    text=example,
                )
                example_obj.save()
