import json
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import CASCADE, SET_NULL, PROTECT, Max, Avg
from django.utils.timezone import utc
from wordfreq import zipf_frequency

from project.helpers.choice_enum import ChoiceEnum


logger = logging.getLogger(__name__)

User = get_user_model()


class List(models.Model):
    name = models.CharField(max_length=300)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    owner = models.ForeignKey(User, related_name='lists', on_delete=CASCADE, null=True)

    sharable = models.BooleanField(default=False, help_text='Able to be shared')

    # @property
    # def stat(self):
    #     return {
    #         'cnt_all': self.words.count(),
    #         'active': self.words.filter(status__in=[Word.Status.Rotation.value, Word.Status.Studying.value]).count(),
    #         'level_1': self.words.filter(status__in=[Word.Status.Level1.value]).count(),
    #         'done': self.words.filter(status__in=[Word.Status.Done.value]).count(),
    #     }

    # @property
    # def err_rate(self):
    #     words = self.words.all()
    #     err = Attempt.objects.filter(word__in=words, result=Attempt.Res.Error.value).count()
    #     cnt = Attempt.objects.filter(word__in=words).count()
    #
    #     sentences = self.sentences.all()
    #     dt = datetime.now() - timedelta(days=2)
    #     err += Attempt.objects.filter(created_at__gte=dt, sentence__in=sentences, result=Attempt.Res.Error.value).count()
    #     cnt += Attempt.objects.filter(created_at__gte=dt,sentence__in=sentences).count()
    #
    #     if cnt > 0:
    #         rate = '%.1f' % (100.0 * err / cnt)
    #     else:
    #         rate = None
    #
    #     return rate
    #
    # @property
    # def attempts_cnt(self):
    #     words = self.words.all()
    #     sentences = self.sentences.all()
    #     return Attempt.objects.filter(word__in=words).count() + Attempt.objects.filter(sentence__in=sentences).count()
    #
    # @property
    # def av_date(self):
    #     words = self.words.all()
    #     now = datetime.now().replace(tzinfo=utc)
    #     size = min(100, len(words))
    #     attempts = Attempt.objects.filter(word__in=words).order_by('-created_at').values('created_at')[:size]
    #     diffs = []
    #     for attempt in attempts:
    #         diffs.append((now - attempt['created_at']).total_seconds())
    #
    #     mean = ''
    #     if diffs and len(diffs):
    #         mean = round(((sum(diffs) / len(diffs)) / 3600 / 24))
    #
    #     return mean

    def __str__(self):
        return '%s' % self.name

    class Meta:
        ordering = ['-id']


class Word(models.Model):

    class Pos(ChoiceEnum):
        Unknown = None
        Noun = 'noun'
        Verb = 'verb'
        Adverb = 'adverb'
        Adjective = 'adjective'
        Preposition = 'preposition'
        Pronoun = 'pronoun'
        Phrasal_verb = 'phrasal_verb'
        Word_plus_preposition = 'word_plus_preposition'
        Adjective_and_preposition = 'adjective_and_preposition'
        Noun_and_preposition = 'noun_and_preposition'
        Verb_and_preposition = 'verb_and_preposition'

    # class Status(ChoiceEnum):
    #     New = None
    #     Rotation = 'rotation'  # находится в ротации в данный момент
    #     Studying = 'studying'  # есть хотя бы один правильный ответ
    #     Level1 = 'level_1'     # пройден первый этап
    #     Done = 'done'  # есть весь набор правильных ответов

    list = models.ManyToManyField('List', related_name='words', blank=True)
    spelling = models.CharField(max_length=300, blank=True)
    part_of_speech = models.CharField(max_length=30, blank=True, null=True, choices=Pos.choices(), default=None)
    transcription = models.CharField(max_length=300, blank=True)

    short_mean = models.CharField(max_length=300, blank=True)
    syn_string = models.CharField(max_length=300, blank=True)

    is_hidden = models.BooleanField(default=False, blank=True)

    # success_cnt = models.IntegerField(default=0)
    # error_cnt = models.IntegerField(default=0)
    #
    # status = models.CharField(max_length=30, blank=True, null=True, choices=Status.choices(), default=None)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    @property
    def zipf(self):
        return zipf_frequency(self.spelling, 'en', wordlist='best')

    # @property
    # def tag(self):
    #     if self.success_cnt == 0 and self.error_cnt == 0:
    #         return 'New'
    #     if self.error_cnt > 0:
    #         return 'Err'
    #     return None
    #
    # @property
    # def score(self):
    #     res = self.success_cnt - min(self.error_cnt * 2, 5)
    #     res = min(5, res)
    #     res = max(0, res)
    #     return res

    def __str__(self):
        return '%s' % self.spelling

    class Meta:
        ordering = ['-id']


class Definition(models.Model):
    word = models.ForeignKey('Word', related_name='definitions', on_delete=CASCADE)
    spelling = models.CharField(max_length=300, blank=True)
    level = models.CharField(max_length=100, blank=True)
    translation = models.CharField(max_length=1000, blank=True)
    interpretation = models.CharField(max_length=1000, blank=True)
    context = models.CharField(max_length=100, blank=True)
    note = models.CharField(max_length=1000, blank=True)

    def __str__(self):
        return '%s' % self.spelling


class Example(models.Model):
    definition = models.ForeignKey('Definition', related_name='examples', on_delete=CASCADE)
    text = models.CharField(max_length=1000, blank=True)
    description = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return '%s' % self.text


class Pronunciation(models.Model):
    # https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000
    # https://www.dictionary.com/browse/fire?s=t
    word = models.ForeignKey('Word', related_name='pronunciations', on_delete=CASCADE)
    audio = models.FileField(upload_to='audio')
    description = models.CharField(max_length=30, blank=True, null=True)
    source = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return '%s: %s' % (self.word, self.description)


class Sentence(models.Model):

    # class Status(ChoiceEnum):
    #     New = None
    #     Rotation = 'rotation'  # находится в ротации в данный момент
    #     Studying = 'studying'  # есть хотя бы один правильный ответ
    #     Level1 = 'level_1'     # пройден первый этап
    #     Done = 'done'          # есть весь набор правильных ответов

    list = models.ManyToManyField('List', related_name='sentences', blank=True)
    text = models.TextField(blank=True)

    # success_cnt = models.IntegerField(default=0)
    # error_cnt = models.IntegerField(default=0)

    is_hidden = models.BooleanField(default=False, blank=True)
    is_flaged = models.BooleanField(default=False, blank=True)

    # status = models.CharField(max_length=30, blank=True, null=True, choices=Status.choices(), default=None)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return '%s' % self.text

    class Meta:
        ordering = ['-id']


class Attempt(models.Model):

    class Res(ChoiceEnum):
        Success = 'success'
        Error = 'error'
        Skip = 'skip'
        Hint = 'hint'

    class Test(ChoiceEnum):
        Unknown = None
        Options = 'options'
        Typing = 'typing'

    user = models.ForeignKey(User, related_name='attempts', on_delete=CASCADE, null=True)

    word = models.ForeignKey('Word', related_name='attempt', on_delete=CASCADE, null=True)
    definition = models.ForeignKey('Definition', related_name='attempt', on_delete=CASCADE, null=True)

    sentence = models.ForeignKey('Sentence', related_name='attempt', on_delete=CASCADE, null=True)
    index = models.IntegerField(default=0)
    answer = models.CharField(max_length=100, null=True)

    result = models.CharField(max_length=30, choices=Res.choices(), default=Res.Success.value)
    test = models.CharField(max_length=30, blank=True, null=True, choices=Test.choices(), default=None)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
