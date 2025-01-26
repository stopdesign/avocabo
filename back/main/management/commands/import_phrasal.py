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
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    )
}

p_verbs = [
    "back away",
    "back off",
    "be back",
    "be off",
    "be out",
    "be over",
    "be up",
    "be up to",
    "blow out",
    "blow up",
    "break down",
    "break in",
    "break into",
    "break off",
    "break out",
    "break up",
    "burst out",
    "call back",
    "calm down",
    "carry on",
    "carry out",
    "catch up",
    "check in",
    "check out",
    "clean up",
    "come across",
    "come along",
    "come back",
    "come by",
    "come down",
    "come forward",
    "come from",
    "come in",
    "come off",
    "come on",
    "come out",
    "come over",
    "come up",
    "count on",
    "cut off",
    "cut out",
    "end up",
    "fall down",
    "fall off",
    "figure out",
    "find out",
    "get along",
    "get around",
    "get away",
    "get back",
    "get down",
    "get in",
    "get off",
    "get along",
    "get out",
    "get over",
    "get through",
    "get up",
    "give up",
    "go along",
    "go around",
    "go away",
    "go back",
    "go by",
    "go down",
    "go in",
    "go off",
    "go on",
    "go out",
    "go over",
    "go through",
    "go up",
    "grow up",
    "hang around",
    "hang on",
    "hang up",
    "help out",
    "hold on",
    "hold out",
    "hold up",
    "keep on",
    "keep up",
    "knock down",
    "knock off",
    "knock out",
    "let in",
    "let out",
    "lie down",
    "line up",
    "look back",
    "look down",
    "look for",
    "look forward to",
    "look out",
    "look over",
    "make out",
    "make up",
    "move in",
    "move on",
    "move out",
    "pass out",
    "pick up",
    "point out",
    "pull away",
    "pull off",
    "pull on",
    "pull out",
    "pull up",
    "put away",
    "put down",
    "put in",
    "put on",
    "put out",
    "put up",
    "run away",
    "run into",
    "run off",
    "run out",
    "run over",
    "set down",
    "set off",
    "set up",
    "settle down",
    "shoot out",
    "show up",
    "shut down",
    "shut up",
    "sit back",
    "sit down",
    "sit up",
    "spread out",
    "stand by",
    "stand out",
    "stand up",
    "stick out",
    "switch off",
    "switch on",
    "take away",
    "take back",
    "take in",
    "take off",
    "take on",
    "take out",
    "take over",
    "take up",
    "throw up",
    "turn around",
    "turn away",
    "turn back",
    "turn down",
    "turn into",
    "turn off",
    "turn on",
    "turn out",
    "turn over",
    "turn up",
    "wake up",
    "walk around",
    "walk away",
    "walk back",
    "walk in",
    "walk off",
    "walk out",
    "walk over",
    "walk up",
    "watch out",
    "wind up",
    "work out",
    "work up",
    "write down",
]

p2_verbs = [
    "put up with",
    "work at",
    "send off",
    "rub into",
    "come down with",
    "stay out",
    "come round",
    "put aside",
    "look through",
    "pass around",
    "stay over",
    "go for",
    "stick together",
    "talk into",
    "face up to",
    "be taken in",
    "deal with",
    "call in",
    "run down",
    "look up to",
    "look forward to",
    "go down with",
    "mix with",
    "stand for",
    "build up",
    "see to",
    "rub on",
    "fall through",
    "stand up for",
    "look at",
    "stay on",
    "head for",
    "bring out",
    "knock over",
    "rub out",
    "turn to",
    "let off",
    "be carried away",
    "keep off",
    "live with",
    "stop over",
    "take out",
    "stick with",
    "come up against",
    "catch on",
    "stand back",
    "get away",
    "get away from",
    "think through",
    "make up for",
    "run on",
    "wear out",
    "come up with",
    "live up to",
    "break through",
    "get at",
    "lock in",
    "pull down",
    "live for",
    "call on",
    "set out",
    "put through",
    "miss out on",
    "keep away",
    "make into",
    "check on",
    "get round to",
    "do away with",
    "work on",
    "clear away",
    "leave out",
    "see through",
    "do without",
    "fit in",
    "fit in with",
    "live on",
    "stand up to",
    "catch up with",
    "clear up",
    "throw out",
    "write up",
    "stay away from",
    "cut across",
    "get away with",
    "get into",
    "set back",
    "get down to",
    "come to",
    "stay up",
    "burst in",
    "get on with",
    "pull in",
    "see off",
    "keep up with",
    "make for",
    "pull over",
    "take down",
    "pay off",
    "care for",
    "keep down",
    "fall for",
    "look on",
    "take to",
    "lock out",
    "pick on",
    "draw up",
    "talk over",
    "get out of",
    "keep back",
]

p3_verbs = [
    "doze off",
    "nod off",
    "rip off",
    "finish off",
    "show off",
    "tell off",
    #     'look forward to', 'drop back', 'call around', 'do away with', 'grow back', 'walk away', 'fill in out',
    #     'look out for', 'walk all over', 'grow out of', 'be left over', 'be rained off', 'work up to', 'log off out',
    #     'log in on', 'fill in out', 'drop by in', 'walk off with', 'not care for', 'look down on', 'pull in into',
    #     'get around', 'get around to', 'pass around round', 'check up on', 'lock in out', 'talk into out of doing'
]


class Command(BaseCommand):
    help = "Test payments"
    cur_word = []
    def_list = None

    def handle(self, *args, **options):
        self.def_list = List.objects.get(id=13)
        self.test("phrasal_verbs.txt")

    def parse(self, text, rx):
        match = re.search(rx, text)
        if match:
            return match.group(1)
        else:
            return ""

    def download_sound(self, path, pronunciation):
        resp = requests.get(path, headers=headers)
        if resp.status_code != requests.codes.ok:
            raise Exception("sound file downloading error")

        fp = BytesIO()
        fp.write(resp.content)

        # Get the filename from the url, used for saving later
        file_name = path.split("/")[-1]

        pronunciation.audio.save(file_name, files.File(fp))

    def load_yandex_data(self, spelling, pos):
        ya_base = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup?key=%s&lang=en-en&text=%s"
        url = ya_base % (settings.YANDEX_DICT_API_KEY, spelling)
        r = requests.get(url)

        res = r.json()
        # print(json.dumps(res, indent=2, ensure_ascii=False))

        try:
            definitions = res["def"][0]["tr"]
        except:
            definitions = []

        means = []
        syns = []

        for definition in definitions:
            if "pos" not in definition:
                continue

            if definition["pos"] != pos:
                continue

            text = definition.get("text")
            syn = definition.get("syn", [])

            for s in syn:
                if spelling not in s["text"]:
                    syns.append(s["text"])

            if spelling in text:
                continue

            means.append(text)

        return means[:5], syns[:5]

    def test(self, filename):
        f = open(filename, "r")

        verbs = p3_verbs

        app_id = settings.OXFORD_DICTIONARIES_APP_ID
        app_key = settings.OXFORD_DICTIONARIES_API_KEY
        params = "fields=definitions%2Cexamples%2Cpronunciations&strictMatch=false"

        # for line in f.readlines():
        #
        #     line = line.strip()
        #     if not line:
        #         continue
        #
        #     spelling, definition, example = line.split('\t')
        #
        #     spelling = spelling.replace('somebody', '').replace('something', '').replace('/', ' ')
        #     spelling = spelling.replace('some place', '')
        #     spelling = spelling.replace(' ', ' ')
        #     spelling = spelling.replace('(or on)', '').replace('(or off)', '')
        #     spelling = spelling.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').strip()
        #     spelling = spelling.replace('by over', 'by')
        #
        #     main_verb, adverb_particle, preposition = (spelling.split(' ') + [None, None, None])[:3]
        #
        #     together = '%s %s' % (main_verb, adverb_particle)
        #     verbs.append(together)

        verbs = list(set(verbs))
        print(len(verbs))

        for verb in verbs[:2000]:
            sleep(0.2)

            url = "https://dictionary.cambridge.org/dictionary/english-russian/%s" % verb.replace(" ", "-")
            # url = 'https://dictionary.cambridge.org/dictionary/english/%s' % verb.replace(' ', '-')

            r = requests.get(url, headers=headers)

            if r.status_code != 200:
                logger.error("bad status_code")
                return

            soup = BeautifulSoup(r.text, "html.parser")

            spelling = self.parse(r.text, r'<div class="h3 di-title cdo-section-title-hw">([^<]*?)</div>')
            # spelling = self.parse(r.text, r'Meaning of <strong>([^<]*?)</strong>')
            pos = self.parse(r.text, r'><span class="pos">([^<]*?)</span>')
            page_id = requests.utils.urlparse(r.url).path.split("/")[-1]

            spelling_clean = spelling.lower() + " "
            spelling_clean = spelling_clean.replace("/", " ").replace("(", " ").replace(")", " ")
            spelling_clean = spelling_clean.replace("-", " ").replace("!", " ")
            spelling_clean = spelling_clean.replace(" sth ", " ").replace(" sb ", " ").replace(" doing ", " ")
            spelling_clean = spelling_clean.replace("to sth/doing sth", " ")
            spelling_clean = spelling_clean.replace("  ", " ").replace("  ", " ").replace("  ", " ").strip()

            if spelling:
                # logger.info('%s\t%s' % (verb, spelling))
                if verb != spelling_clean:
                    logger.warning(".%s.\t.%s.\t.%s." % (verb, spelling, spelling_clean))
                    # url = 'https://od-api.oxforddictionaries.com:443/api/v2/entries/en-us/%s?%s' % (verb, params)
                    # r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
                    # print(json.dumps(r.json(), indent=2, ensure_ascii=False))
                    continue
            else:
                logger.error(verb)
                continue

            spelling = verb
            pos = "phrasal_verb"
            pos_yandex = "verb"

            ##
            ##
            ##
            ##
            ##
            ##

            entry_body = soup.find("div", {"class": "normal-entry-body"})
            idiom_body = soup.find("div", {"class": "idiom-body"})

            pron_info = soup.select(".di-info > .pron-info")
            prons = []
            for el in pron_info:
                try:
                    region = el.select(".region")[0].get_text(strip=True)
                except IndexError:
                    region = None
                if el.select(".audio_play_button"):
                    mp3 = el.select(".audio_play_button")[0]["data-src-mp3"]
                    prons.append(
                        {
                            "url": "https://dictionary.cambridge.org" + mp3,
                            "region": region,
                            "source": "dictionary.cambridge.org",
                        }
                    )

            # print('prons:', json.dumps(prons, indent=2))

            try:
                transcription = soup.select(".di-info .pron .ipa")[0].get_text(strip=True)
            except IndexError:
                transcription = ""

            # удаление экземпляров этого слова, которые уже есть в списке
            for same_word in Word.objects.filter(spelling__iexact=spelling, part_of_speech__iexact=pos):
                self.def_list.words.remove(same_word)
                if same_word.list.count() == 0:
                    same_word.delete()

            means, syns = self.load_yandex_data(spelling, pos_yandex)
            means_str = ("; ".join(means)).strip().strip(";")
            syns_str = ("; ".join(syns)).strip().strip(";")

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

            pronunciations_saved = []
            for pronunciation in prons:
                if pronunciation["url"] not in pronunciations_saved:
                    pronunciations_saved.append(pronunciation["url"])
                    pro_obj = Pronunciation(
                        word=word,
                        description=pronunciation["region"],
                        source=pronunciation["source"],
                    )
                    pro_obj.save()
                    self.download_sound(pronunciation["url"], pro_obj)

            if entry_body:
                title = ""

                for sense_block in entry_body.select(".sense-block") or []:
                    notes = []

                    s = sense_block.select(".sense-head > .sense-title")
                    if s:
                        title = s[0].get_text(strip=True, separator=" ")

                    xref = ""
                    s = sense_block.select(".sense-body .epp-xref")
                    if s:
                        xref = s[0].get_text(strip=True)

                    phrase_title = None
                    s = sense_block.select(".sense-body .phrase-title")
                    if s:
                        phrase_title = s[0].get_text(strip=True)

                    phrase_info = None
                    s = sense_block.select(".sense-body .phrase-info")
                    if s:
                        phrase_info = s[0].get_text(strip=True)
                        notes.append(phrase_info)

                    translation = None
                    s = sense_block.select(".sense-body .trans")
                    if s:
                        translation = s[0].get_text(strip=True, separator=" ")

                    interpretation = None
                    s = sense_block.select(".sense-body .def")
                    if s:
                        interpretation = s[0].get_text()

                    examp = []
                    s = sense_block.select(".sense-body .examp")
                    for e in s:
                        examp.append(
                            {
                                "text": (
                                    e.find("span", {"class": "eg"})
                                    .get_text(strip=True, separator=" ")
                                    .strip(".")
                                    .strip()
                                ),
                            }
                        )

                    # print(title)
                    # print(xref)
                    # print(trans)
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
                        note=("; ".join(notes)).strip("; "),
                    )
                    definition_obj.save()

                    for example in examp:
                        example_obj = Example(
                            definition=definition_obj,
                            text=example["text"],
                        )
                        example_obj.save()
