#!/usr/bin/python
#coding: utf-8

import json
import requests
from collections import OrderedDict

f = open('3000.txt', 'r')
words_3000 = f.read().strip().split('\n')
f.close()

f = open('mart.txt', 'r')

#all_text = f.read().decode('string-escape').decode('utf-8')
all_text = f.read().decode('utf-8').strip().replace(u'—','-').encode('latin-1', 'ignore')  #[399200:399300]

f.close()

words = {}

for word in all_text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('?', ' ').split(' '):
    word = word.strip('''*,"'();:.-!?''').lower()

    if len(word) < 4 or '-' in word or any(i.isdigit() or i == '.' for i in word):
        continue

    if word not in words:
        words[word] = 0
    words[word] += 1

for word in words:

    if word in words_3000:
        words[word] = -2

    if word[-3:] == 'ing' and word[:-3] in words:
        words[word] = -1

    if word[-2:] == 'ed' and word[:-2] in words:
        words[word] = -1

    if word[-1:] == 's' and word[:-1] in words:
        words[word] = -1


words = {k: v for k, v in words.values() if 20 > v > 0}

words = OrderedDict(sorted(words.items()))

#for word in words:
#    trans = requests.get('https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.20160502T232222Z.dbb4d3ba97834727.576bac7031c23a61866b8f3eefcc8deabef60428&text=%s&lang=en-ru&format=html' % word)
#    w_trans = ', '.join(trans.json()['text'])
#    print word, w_trans
#    f = open('res.txt', 'a+')
#    f.write(('%s\t%s\n' % (word, w_trans)).encode('utf-8'))
#    f.close()

print(json.dumps(words, indent=4))
print()
print(len(words))


