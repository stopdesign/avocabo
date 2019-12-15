import sys
import json
import logging
from io import BytesIO
from time import sleep
import requests
from django.core import files
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.core.management.base import BaseCommand

from main.models import Word, Definition, Example, Pronunciation, List

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Test payments'

    def handle(self, *args, **options):

        self.test('2.txt')

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

        app_id = settings.OXFORD_DICTIONARIES_APP_ID
        app_key = settings.OXFORD_DICTIONARIES_API_KEY
        word_id = 'example'
        params = 'fields=definitions%2Cexamples%2Cpronunciations&strictMatch=true'
        url = 'https://od-api.oxforddictionaries.com:443/api/v2/entries/en-us/%s?%s' % (word_id.lower(), params)
        r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})

        # https://od-api.oxforddictionaries.com:443/api/v2/entries/en-us/fire?fields=definitions%2Cexamples%2Cpronunciations&strictMatch=true
        # The /senses/ endpoint returns a list of senses (i.e. meanings of words) documented in the OED, optionally filtered by a range of parameters.
        # /quotations/

        # cambridge API — хуйня
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

    def download_sound(self, path, pronunciation):

        resp = requests.get(path)
        if resp.status_code != requests.codes.ok:
            raise Exception('sound file downloading error')

        fp = BytesIO()
        fp.write(resp.content)

        # Get the filename from the url, used for saving later
        file_name = path.split('/')[-1]

        pronunciation.audio.save(file_name, files.File(fp))


    def test(self, filename):

        f = open(filename, 'r')

        # all_text = f.read().decode('string-escape').decode('utf-8')
        all_text = f.read().strip().replace(u'—', '-')  # [399200:399300]

        def_list = List.objects.get(id=4)

        words = []

        for word in all_text.replace('\r', ' ').replace('\t', ' ').replace('?', ' ').strip().split('\n'):
            word = word.strip('''*,"'();:.-!?''').lower()

            if len(word) < 4 or any(i.isdigit() or i == '.' for i in word):
                continue

            words.append(word)

        for spelling in words[:2000]:

            # print('\n')
            # print(spelling)
            sleep(0.1)

            app_id = settings.OXFORD_DICTIONARIES_APP_ID
            app_key = settings.OXFORD_DICTIONARIES_API_KEY
            word_id = spelling
            params = 'fields=definitions%2Cexamples%2Cpronunciations&strictMatch=true'
            url = 'https://od-api.oxforddictionaries.com:443/api/v2/entries/en-us/%s?%s' % (word_id.lower(), params)
            r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})

            res = r.json()
            # print(json.dumps(res, indent=2, ensure_ascii=False))

            # удаление экземпляров этого слова, которые уже есть в словаре
            # Word.objects.filter(spelling__iexact=spelling).delete()

            word = Word(spelling=spelling)

            try:
                lexs = res['results'][0]['lexicalEntries']
            except:
                logger.error(spelling)
                continue

            # добавляю слово в список
            word.save()
            def_list.words.add(word)

            transcription = ''
            pronunciations = []

            for lex in lexs:
                spelling = lex['text']
                pos = lex['lexicalCategory']['id']
                for pro in lex.get('pronunciations', []):
                    if (
                        pro['phoneticNotation'] == 'IPA' and
                        'audioFile' in pro and
                        'American English' in pro.get('dialects', [])
                    ):
                        pronunciations.append({
                            'url': pro['audioFile'],
                            'source': 'oxforddictionaries',
                            'description': 'American English',
                        })
                        transcription = pro['phoneticSpelling']
                if len(lex.get('entries', [])) != 1:
                    logger.error('NO ENTRIES FOR: %s' % spelling)
                    continue

                for definition in lex['entries'][0]['senses']:
                    description = '; '.join(definition['definitions']).strip().strip(';')
                    translation = None
                    examples = []
                    for ex in definition.get('examples', []):
                        examples.append({
                            'text': ex['text'],
                        })

                    # print(spelling, pos, transcription)
                    # print('description:', description)
                    # print('translation:', translation)
                    # print('examples:', json.dumps(examples, indent=2, ensure_ascii=False))
                    # print()

                    definition_obj = Definition(
                        word=word,
                        spelling=spelling,
                        transcription=transcription,
                        interpretation=description,
                        # translation=translation,
                        part_of_speech=pos,
                    )
                    definition_obj.save()

                    for example in examples:
                        example_obj = Example(
                            definition=definition_obj,
                            text=example['text']
                        )
                        example_obj.save()

            pronunciations_saved = []
            for pronunciation in pronunciations:
                if pronunciation['url'] not in pronunciations_saved:
                    pronunciations_saved.append(pronunciation['url'])
                    pro_obj = Pronunciation(
                        word=word,
                        description=pronunciation['description'],
                        source=pronunciation['source'],
                    )
                    pro_obj.save()
                    self.download_sound(pronunciation['url'], pro_obj)

            continue

            ya_base = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=%s&lang=en-ru&text=%s'
            url = ya_base % (settings.YANDEX_DICT_API_KEY, spelling)
            r = requests.get(url)

            res = r.json()
            # print(json.dumps(res, indent=2, ensure_ascii=False))

            # # удаление экземпляров этого слова, которые уже есть в словаре
            # Word.objects.filter(spelling__iexact=spelling).delete()
            #
            # word = Word(spelling=spelling)

            # добавляю слово в список
            word.save()
            def_list.words.add(word)

            for definition in res['def']:

                if 'ts' not in definition:
                    continue

                spelling = definition.get('text', word.spelling)
                pos = definition.get('pos')
                transcription = definition['ts']
                trs = definition.get('tr', [])

                translations = []
                for tr in trs:
                    if tr.get('text'):
                        translations.append(tr.get('text'))

                means = []
                for tr in trs:
                    for mean in tr.get('mean', []):
                        means.append(mean['text'])

                examples = []
                for tr in trs:
                    for ex in tr.get('ex', []):
                        examples.append({
                            'text': ex['text'],
                            'trans': ('; '.join([t['text'] for t in ex['tr']])).strip().strip(';'),
                        })

                description = '; '.join(means).strip().strip(';')
                translation = '; '.join(translations).strip().strip(';')

                # print(spelling, pos, transcription)
                # print('description:', description)
                # print('translation:', translation)
                # print('examples:', json.dumps(examples, indent=2, ensure_ascii=False))
                # print()

                definition_obj = Definition(
                    word=word,
                    spelling=spelling,
                    transcription=transcription,
                    interpretation=description,
                    translation=translation,
                    part_of_speech=pos,
                )
                definition_obj.save()

                for example in examples:
                    example_obj = Example(
                        definition=definition_obj,
                        text=example['text']
                    )
                    example_obj.save()
