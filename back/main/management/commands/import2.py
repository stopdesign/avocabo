import math
import re
import sys
import json
import logging
from io import BytesIO
from time import sleep
from bs4 import BeautifulSoup
import fake_useragent
import requests
from django.core import files
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand
from fake_useragent import UserAgent

from main.models import Word, Definition, Example, Pronunciation, List

logger = logging.getLogger(__name__)


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
}


class Command(BaseCommand):

    help = 'Test payments'
    cur_word = []
    def_list = None
    add_empty = False

    def handle(self, *args, **options):

        self.def_list = List.objects.get(id=22)
        self.add_empty = True
        self.test('dariko_1.txt')

    def send_waves(self):
        pass

        # https://tech.yandex.com/dictionary/doc/dg/reference/lookup-docpage/
        # 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=APIkey&lang=en-ru&text=time'  # pos

        # cambridge — звук
        # нужно парсить: https://dictionary.cambridge.org/dictionary/english/fire-certificate
        # American pronunciation" data-src-mp3="****"
        #
        # https://dictionary.cambridge.org/media/english/us_pron/f/fis/fish_/fish.mp3
        # https://dictionary.cambridge.org/media/english/us_pron/u/usf/usfin/usfinal023.mp3

        # oxford — звук
        # https://www.oxfordlearnersdictionaries.com/media/english/us_pron/f/fin/finis/finish__us_1.mp3
        # https://www.oxfordlearnersdictionaries.com/media/english/us_pron/f/fir/firef/firefighter__us_1.mp3
        #
        # API — есть ключ
        # https://od-api.oxforddictionaries.com:443/api/v2/entries/en-us/fire?fields=definitions%2Cexamples%2Cpronunciations&strictMatch=true
        # The /senses/ endpoint returns a list of senses (i.e. meanings of words) documented in the OED, optionally filtered by a range of parameters.
        # /quotations/

        # Хороший словарь, похож на dictionary.cambridge.org, но примеров сильно больше
        # https://www.collinsdictionary.com/dictionary/english/lose-weight-gain-put-on-weight

        # cambridge — хуйня
        # https://dictionary-api.cambridge.org/ — дорого, но есть тестовый период 3000 calls in the 30 days.
        # и только для https://dictionary-api.cambridge.org/api/demo

        # Куча ссылок на словарные API, 50 штук
        # https://www.programmableweb.com/category/dictionary/api

        # 10 разных словарных API с описанием
        # https://blog.rapidapi.com/dictionary-apis/

        # TWINWORD
        # https://www.twinword.com/api/word-dictionary.php
        # Простые эндпоинты. Хорошие расшифровки, но у примеров не указана часть речи
        #
        # (nou) the event of something burning (often destructive)
        # (nou) the act of firing weapons or artillery at an enemy
        # (nou) the process of combustion of inflammable materials producing heat and light and (often) smoke
        # (nou) a fireplace in which a relatively small fire is burning
        # (nou) once thought to be one of four elements composing the universe (Empedocles)
        # (nou) feelings of great warmth and intensity\n(nou) fuel that is burning and is used as a means for cooking
        # (nou) a severe trial
        # (nou) intense adverse criticism
        #
        # (vrb) start firing a weapon
        # (vrb) cause to go off
        # (vrb) bake in a kiln so as to harden
        # (vrb) terminate the employment of; discharge from an office or position
        # (vrb) go off or discharge
        # (vrb) drive out or away by or as if by fire
        # (vrb) call forth (emotions, feelings, and responses)
        # (vrb) destroy by fire
        # (vrb) provide with fuel

        # ЛЕММЫ
        # разбирает текст на леммы
        # 500 запросов в месяц, но можно передавать кучу текста за раз
        # Полезно прогнать слова через это
        # https://www.twinword.com/api/lemmatizer.php

        # Синонимы, похожее звучание, похожее написание, связь между словами...
        # База WordNet
        # лимиты — 100 тысяч в сутки
        # https://www.datamuse.com/api/

    def download_sound(self, path, pronunciation):

        resp = requests.get(path, headers=headers)
        if resp.status_code != requests.codes.ok:
            raise Exception('sound file downloading error')

        fp = BytesIO()
        fp.write(resp.content)

        # Get the filename from the url, used for saving later
        file_name = path.split('/')[-1]

        pronunciation.audio.save(file_name, files.File(fp))

    def parse(self, text, rx):
        match = re.search(rx, text)
        if match:
            return match.group(1)
        else:
            return ''

    def test(self, filename):

        f = open(filename, 'r')

        # all_text = f.read().decode('string-escape').decode('utf-8')
        all_text = f.read().strip().replace(u'—', '-')  # [399200:399300]

        words = []

        for word in all_text.replace('\r', ' ').replace('\t', ' ').replace('?', ' ').strip().split('\n'):
            word = word.strip('''*,"'();:.-!?''').lower()

            if len(word) < 3 or any(i.isdigit() or i == '.' for i in word):
                continue

            words.append(word)

        # ua = UserAgent()

        for spelling in words[:1000]:

            print('\n')
            logger.debug(spelling)
            sleep(0.5)

            spelling = spelling.strip()

            self.cur_word = []
            res = self.parse_pos(spelling)

            # если слово не нашлось в словаре — добавляю его без заполнения данных
            if self.add_empty and spelling and not res:
                word = Word(spelling=spelling, part_of_speech=None)
                word.save()
                self.def_list.words.add(word)

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

        for definition in definitions:
            if 'pos' not in definition:
                continue

            if definition['pos'] != pos:
                continue

            text = definition.get('text')
            syn = definition.get('syn', [])

            for s in syn:
                if spelling not in s['text']:
                    syns.append(s['text'])

            if spelling in text:
                continue

            means.append(text)

        return means[:5], syns[:5]

    def parse_pos(self, url_spelling):

        url = 'https://dictionary.cambridge.org/dictionary/english-russian/%s' % url_spelling

        r = requests.get(url, headers=headers)

        if r.status_code != 200:
            return

        soup = BeautifulSoup(r.text, 'html.parser')

        spelling = self.parse(r.text, r'<div class="h2 tw-bw dhw dpos-h_hw di-title ">([^<]*?)</div>')
        pos = self.parse(r.text, r'><span class="pos dpos"[^>]*?>([^<]*?)</span>')
        page_id = requests.utils.urlparse(r.url).path.split('/')[-1]

        # исключение повторной загрузки той же страницы
        if page_id in self.cur_word:
            return
        self.cur_word.append(page_id)

        if spelling:
            logger.warning('=== %s / %s / %s ===' % (spelling, pos, page_id))
        else:
            logger.error('Word "%s" was not found' % url_spelling)
            return False

        # поиск слова, о котором эта страница
        try:
            word_bs = soup.find('div', {'class': 'h2 tw-bw dhw dpos-h_hw di-title'}).get_text(strip=True)
            try:
                pos_bs = soup.select('span.posgram > span.pos')[0].get_text(strip=True)
            except IndexError:
                logger.warning('Word "%s" is not a word, %s' % (url_spelling, r.url))
        except AttributeError:
            logger.error('Word "%s" was not found' % url_spelling)
            return False

        # проверка, что слово совпадает после всех изменений
        if abs(len(url_spelling) - len(spelling)) > 3:
            logger.warning('Not exactly: "%s" != "%s"' % (url_spelling, spelling))

        # что это за хуйня?
        # ссылка на другую статью?
        for el in soup.select('.grad-trans-pseudo li'):
            linked_word = el.select('b')[0].get_text(strip=True, separator=' ')
            linked_word_pos = None
            s = el.select('.pos')
            if s:
                linked_word_pos = s[0].get_text(strip=True, separator=' ')
            else:
                linked_word_pos = 'phrase'
                # logger.warning('phrase?')
                # print(el)
                # print()
            link = el.find('a')
            if word_bs == linked_word and link:
                # logger.warning(linked_word)
                # logger.debug(linked_word_pos)
                new_url = link['href'].split('/')[-1]
                # logger.debug(new_url)
                # print()
                if new_url not in self.cur_word:
                    self.parse_pos(new_url)

        entry_body = soup.find('div', {'class': 'normal-entry-body'})

        # не обрабатываются
        idiom_body = soup.find('div', {'class': 'idiom-body'})

        # произношение
        pron_info = soup.select('.di-info > .pron-info')
        prons = []
        for el in pron_info:
            try:
                region = el.select('.region')[0].get_text(strip=True)
            except IndexError:
                region = None
            if el.select('.audio_play_button'):
                mp3 = el.select('.audio_play_button')[0]['data-src-mp3']
                prons.append({
                    'url': 'https://dictionary.cambridge.org' + mp3,
                    'region': region,
                    'source': 'dictionary.cambridge.org',
                })

        # print('prons:', json.dumps(prons, indent=2))

        try:
            transcription = soup.select('.di-info .pron .ipa')[0].get_text(strip=True)
        except IndexError:
            transcription = ''

        # удаление экземпляров этого слова, которые уже есть в списке
        for same_word in Word.objects.filter(spelling__iexact=spelling, part_of_speech__iexact=pos):
            self.def_list.words.remove(same_word)
            if same_word.list.count() == 0:
                same_word.delete()

        means, syns = self.load_yandex_data(spelling, pos)
        means_str = ('; '.join(means)).strip().strip(';')
        syns_str = ('; '.join(syns)).strip().strip(';')

        # добавляю слово в список
        word = Word(
            spelling=spelling,
            part_of_speech=pos,
            transcription=transcription,
            short_mean=means_str,
            syn_string=syns_str,
        )
        word.save()
        self.def_list.words.add(word)

        # произношения
        pronunciations_saved = []
        for pronunciation in prons:
            if pronunciation['url'] not in pronunciations_saved:
                pronunciations_saved.append(pronunciation['url'])
                pro_obj = Pronunciation(
                    word=word,
                    description=pronunciation['region'],
                    source=pronunciation['source'],
                )
                pro_obj.save()
                self.download_sound(pronunciation['url'], pro_obj)

        # значения
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
                    examp.append({
                        'text': e.find('span', {'class': 'eg'}).get_text(strip=True, separator=' ').strip('.').strip(),
                    })

                # print(title)
                # print(xref)
                # # print(trans)
                # print(interpretation)
                # print(json.dumps(examp, indent=2))
                # print()

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

        if idiom_body:
            logger.warning('IDIOM')

        return word





