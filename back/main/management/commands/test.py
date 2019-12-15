import math
import random
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
import jellyfish
from main.models import Word, Definition, Example, Pronunciation, List

logger = logging.getLogger(__name__)


good_words = ['back up','be carried away','be taken in','blow up','break down','break in','break off','break out','break through','break up','bring out','bring up','build up','burst in','burst out','call in','call off','call on','care for','carry on','catch on','catch up with','check on','check out','clear away','clear up','come across','come along','come down','come down with','come off','come on','come out','come round','come to','come up','come up against','come up with','count on','cross out','cut across','cut down','cut out','deal with','do away with','do up','do without','draw up','face up to','fall for','fall out','fall through','fit in (with)','get across','get at','get away (from)','get away with','get down','get down to','get in','get into','get on with','get out','get out of','get over','get round to','get through','get together','get up','give away','give in','give up','go ahead','go by','go down with','go for','go off','go on','go over','go through','hand over','head for','hold back','hold on','keep away','keep back','keep down','keep off','keep up with','knock down','knock out','knock over','leave out','let down','let off','let out','live for','live on','live up to','live with','lock in','lock out','look at','look back','look forward to','look into','look on','look out','look through','look up to','make for','make into','make out','make up','make up for','miss out on','mix up','mix with','pass around','pass away','pass out','pay off','pick on','pick up','point out','pull down','pull in','pull out','pull over','pull up','put aside','put down','put off','put on','put out','put through','put up','put up with','rub into','rub on','rub out','run away','run down','run into','run on','run out (of)','run over','see off','see through','see to','send off','set back','set off','set out','set up','show off','stand back','stand by','stand for','stand out','stand up','stand up for','stand up to','stay away from','stay on','stay out','stay over','stay up','stick out','stick to','stick together','stick with','stop over','take after','take away','take down','take in','take off','take on','take out','take over','take to','take up','talk into','talk over','think over','think through','throw away','throw out','throw up','try out','turn back','turn down','turn out','turn to','turn over','turn up','watch out','wear off','wear out','work at','work on','work out','write up']


class Command(BaseCommand):

    help = 'Test payments'
    cur_word = []
    def_list = None

    def handle(self, *args, **options):
        self.def_list = List.objects.get(id=12)
        self.test()

    def find_by_distance(self, verb, text):
        words = text.split(' ')
        max_val = 0.1
        final = None
        for word in words:
            word_clean = word.lower().strip()
            if word_clean[-3:] == 'ing':
                word_clean = word_clean[:-3]
            res = jellyfish.jaro_distance(word_clean, verb)
            if res > max_val:
                final = word
                max_val = res
            # res = jellyfish.levenshtein_distance(word, verb)
            # res = jellyfish.damerau_levenshtein_distance(word, verb)
            # print(word, verb, res)
        return final

    # def test(self):
    #     l12 = self.def_list
    #     my_words = list(l12.words.values_list('spelling', flat=True))
    #
    #     print('my_words', len(set(my_words)))
    #     print('good_words', len(set(good_words)))
    #     # print(len(set(my_words+good_words)))
    #     print(len(set(good_words) - set(my_words)))
    #
    #     for w in set(good_words) - set(my_words):
    #         print(w)


    def test(self):

        l12 = self.def_list

        not_found = []

        all_verbs = []
        all_adverb_particle = []
        for w in l12.words.order_by('?')[:50]:
            verb = w.spelling.split(' ')[0]
            adverb_particle = w.spelling.split(' ')[1]
            all_verbs.append(verb)
            all_adverb_particle = all_adverb_particle + adverb_particle.split('/')

        all_verbs = list(set(all_verbs))
        all_adverb_particle = list(set(all_adverb_particle))

        for w in l12.words.order_by('-id')[:5]:
            verb = w.spelling.split(' ')[0]
            adverb_particle = w.spelling.split(' ')[1]
            try:
                preposition = w.spelling.split(' ')[2]
            except IndexError:
                preposition = None
            for d in w.definitions.all():

                for e in d.examples.all():

                    e_text = ' ' + e.text
                    # e_text = e_text.replace(' ' + adverb_particle, ' __%s__' % adverb_particle)
                    for ap in adverb_particle.split('/'):
                        if ap in e_text:
                            e_text = e_text.replace(' ' + ap, ' ____')
                            adverb_particle = ap
                            break
                    e_text = e_text.lstrip(' ')

                    res = self.find_by_distance(verb, e_text)

                    if res:
                        if verb in e_text.lower():
                            # logger.debug('\n' + e_text.replace(res, '__%s__' % res))
                            print('' + e_text.replace(res, '____'))
                        else:
                            # logger.warning('\n' + e_text.replace(res, '__%s__' % res))
                            print('' + e_text.replace(res, '____'))
                    else:
                        logger.error('err: %s \t %s' % (verb, e_text))
                        continue

                    if preposition:
                        e_text = e_text.replace('____ %s' % preposition, '____ ____')

                    print(w.spelling)
                    print(d.translation, '\n')

                    # варианты ответов
                    random.shuffle(all_verbs)
                    random.shuffle(all_adverb_particle)

                    v_options = ([verb] + all_verbs)[:5]
                    p_options = ([adverb_particle] + all_adverb_particle)[:5]

                    random.shuffle(v_options)
                    random.shuffle(p_options)

                    for i in range(0, 5):
                        print(v_options[i], '\t', p_options[i])
                    print()
                    print()
                    print()