import nltk
import logging
import json
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

    cur_word = []
    def_list = None

    pattern_to = ['VB', 'TO', 'VB']
    pattern_ing = ['VB', 'VBG']

    banned = ['be', 'have', 're', 'get', 'there', 'use', 'bed', 'fun']

    def handle(self, *args, **options):

        self.test('hp.txt')
        # self.test('mart.txt')
        # self.test('full.txt')
        # self.test('training.1600000.processed.noemoticon.csv')

    def search_for_pattern(self, words, tags, pattern):
        found_index = sub_index(tags, pattern)
        if found_index is not None:
            first_word = words[found_index].lower()
            if first_word not in self.banned and len(first_word) >= 3:
                # print(words[found_index:found_index + len(pattern)])
                return clean(first_word), map(clean, list(words[found_index:found_index + len(pattern)])), words

    def test(self, filename):

        f = open(filename, 'r')

        all_text = f.read(1000000).strip().replace(u'—', '-')  # [399200:399300]

        # all_text = all_text.replace(' "', '\n"')
        # all_text = all_text.replace('. ', '.\n')
        all_text = all_text.replace('Mr.', 'Mr')
        all_text = all_text.replace('Ms.', 'Ms')
        all_text = all_text.replace('Mrs.', 'Mrs')
        # all_text.replace('!', '!/')
        # all_text.replace('?', '?/')
        # all_text.replace('.', './')
        # all_text.replace(';', ';/')

        to = []
        ing = []

        words_to = {}
        words_ing = {}

        words_count = 0

        for sentence in all_text.split('\n'):

            # для твиттера
            if len(sentence.split('","')) == 6:
                sentence = sentence.split('","')[5]
                sentence = sentence.rstrip('"').rstrip()

            if len(sentence) > 550 or len(sentence) < 10:
                continue

            # print(sentence)

            tokens = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(tokens)

            if not tagged:
                continue

            words, tags = zip(*tagged)

            # # print(tags)
            # for word in words:
            #     if len(word) > 1:
            #         words_count += 1
            #
            # res = self.search_for_pattern(words, tags, self.pattern_to)
            # if res:
            #     words_to.setdefault(res[0], []).append(sentence)
            #     to.append(res[1])
            #
            # res = self.search_for_pattern(words, tags, self.pattern_ing)
            # if res:
            #     words_ing.setdefault(res[0], []).append(sentence)
            #     ing.append(res[1])

            res = ''

            for tt in tagged:
                if tt[1] in ['VB', 'VBG']:
                    res += D_ + tt[0] + _D
                else:
                    res += tt[0]
                res += ' '

            print(res)
            print()

        # words_to = list(set(words_to))
        # words_ing = list(set(words_ing))

        print('words_count:', words_count)

        # print('\n\nTO')
        #
        # for word in words_to:
        #     print('\n', word)
        #     for ex in words_to[word]:
        #         print('   ', ex)

        # counts = Counter(words_to)
        # for w in counts.most_common(10000):
        #     if w[1] > 2:
        #         print(w[0], '—', w[1])

        # for w in to:
        #     print(' '.join(w))

        # print('\n\nING')
        # # print(words_ing)
        #
        # for word in words_ing:
        #     if len(words_ing[word]) < 5:
        #         continue
        #
        #     print('\n\n', B_, word, '+ V-ING', _B)
        #     for ex in words_ing[word][:5]:
        #         print('   ', ex.replace(word, M_ + word + _M))
        #
        #     if word in words_to:
        #         print('\n', D_, word, '+ TO + V', _D)
        #         for ex in words_to[word][:5]:
        #             print('   ', ex.replace(word, M_ + word + _M))

        # counts = Counter(words_ing)
        # for w in counts.most_common(10000):
        #     if w[1] > 2:
        #         print(w[0], '—', w[1])

        # for w in ing:
        #     print(' '.join(w))

        print('\n\n')

