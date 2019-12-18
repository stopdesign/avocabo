import random
import re
from datetime import datetime, timedelta
from time import sleep
import jellyfish
from collections import Counter

from django.contrib.auth.models import AnonymousUser
from django.template.response import TemplateResponse
from django.db.models import F, Count, Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from main.serializers import ListSerializer, ListDetailsSerializer, WordSerializer, AttemptSerializer
from main.models import List, Word, Attempt, Sentence, User
import json
import logging
from django.http import HttpResponse, Http404

logger = logging.getLogger(__name__)


SOME_PREPS = [
    'of', 'with', 'at', 'from', 'into', 'to', 'in', 'for', 'on', 'by', 'about', 'like', 'up', 'after', 'over', 'before',
    'since', 'under', 'through', 'within', 'across', 'behind', 'beyond', 'out', 'around', 'down', 'off', 'above'
]


def index(request):
    """
    Главная страница (куча списков и статистика по ответам в день)
    """

    dt = datetime.now() - timedelta(days=14)
    counts = Attempt.objects.filter(created_at__gte=dt).extra({
        'dt': 'date(created_at)'}).values('dt').order_by('dt').annotate(cnt=Count('id'))

    user_rotation = None

    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.pk)
        user.update_rotation()
        user_rotation = user.rotation

        print('user_rotation', user_rotation)

    context = {
        'counts': json.dumps(list(counts), indent=2),
        'lists': List.objects.all(),
        'user_rotation': user_rotation,
    }
    return TemplateResponse(request, 'index.html', context)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def words(request, list_id):
    """
    Список слов одной темы, HTML
    """
    try:
        words_list = List.objects.get(id=list_id)
    except:
        return Http404()

    words = words_list.words.order_by('id')

    # TODO: персонализировать статистику в списке?

    # статистика по ошибкам в попытках
    # sentences = words_list.sentences.all()
    # attempts = Attempt.objects.filter(sentence__in=sentences).order_by('created_at')
    # for chunk in chunks(attempts, 50):
    #     cnt = 0
    #     err = 0
    #     for attempt in chunk:
    #         if attempt.result == Attempt.Res.Error.value:
    #             err += 1
    #         cnt += 1
    #         # print(attempt.created_at, attempt.result)
    #     print(chunk[-1].created_at.date(), '\t', '%.1f' % (100.0 * err / cnt))

    # error_cnt = words_list.sentences.values_list('error_cnt', flat=True)
    # cnt = dict(Counter(error_cnt))
    # for n, c in cnt.items():
    #     print('%s\t%s' % (n, c))

    context = {
        'list': words_list,
        'words': words,
    }
    return TemplateResponse(request, 'words.html', context)


class ListAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = List.objects.get(pk=id)
            serializer = ListDetailsSerializer(item, user=request.user)
            return Response(serializer.data)
        except List.DoesNotExist:
            return Response(status=404)


class ListAPIListView(APIView):

    def get(self, request, format=None):

        # Если анонимный юзер — показываем все публичные (sharable) темы
        # Если юзер залогинен, то он видит:
        #   все публичные темы
        #   свои личные темы (owner)
        #   свои подписки (subscriptions)

        if request.user.is_authenticated:
            subscriptions = request.user.user_subscriptions.values_list('id', flat=True)
            items = List.objects.filter(id__in=subscriptions)

            print('subscriptions', subscriptions)
            print('public', List.objects.filter(sharable=True).values_list('id', flat=True))
            print('count', items.count(), '/', List.objects.count())
        else:
            items = List.objects.filter(sharable=True)

        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = ListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class WordAPIView(APIView):

    def get(self, request, id, format=None):
        try:
            item = Word.objects.get(pk=id)
            serializer = WordSerializer(item)
            return Response(serializer.data)
        except Word.DoesNotExist:
            return Response(status=404)


class Test1APIView(APIView):

    def get(self, request, id, format=None):

        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.pk)
            user.update_rotation()
            rotation = user.rotation
        else:
            user = AnonymousUser()
            rotation = '2488 2490 2270 2543 2612 1369 2322 1681 1986 1626'  # 2638  2496  2358  1428

        rotation = rotation.strip().split(' ')
        rotation = filter(None, rotation)
        rotation = [int(r) for r in rotation]

        print('request', request)

        print('request.user', request.user)
        print('rotation', rotation)

        # статусы, подходящие для этого теста
        words_to_test = Word.objects.filter(id__in=rotation).order_by('?')
        all_words = Word.objects.all().exclude(definitions=None).order_by('?').values_list('spelling', flat=True)[:300]

        quizlist = []

        for word in words_to_test:
            definitions = word.definitions.all().order_by('?')
            if not definitions:
                continue

            definition = definitions[0]

            options = list(set(all_words))
            try:
                options.remove(word.spelling)
            except ValueError:
                pass

            options = random.sample(options, 4)
            options.append(word.spelling)
            random.shuffle(options)

            pronunciation = word.pronunciations.first()
            if pronunciation:
                pronunciation_url = pronunciation.audio.url
            else:
                pronunciation_url = None

            quizlist.append({
                'word': WordSerializer(word).data,
                'word_id': word.id,
                'definition_id': definition.id,
                'quiz': definition.translation or definition.interpretation,
                'options': options,
                'answer': options.index(word.spelling),
                'pronunciation': pronunciation_url,
            })

        data = {
            'results': quizlist,
        }

        return HttpResponse(
            json.dumps(data, ensure_ascii=False),
            status=200,
            content_type='application/json; charset=utf-8')


class TestTensesAPIView(APIView):

    def get(self, request, format=None):

        data = '''Actions In Stories	Past Simple
Unfinished Actions Now	Present Continuous
Future Timetables	Present Simple
Story Background	Past Continuous
Unreal Things In The Past	Past Perfect
Finished Time Period	Past Simple
Details Of News	Past Simple
Short Actions Now	Present Simple
How Much Time from Moment (past) to Now	Present Perfect
Temporary Habits	Present Continuous
Permanent Situations	Present Simple
Emphasis Of Length Of Action	Past Continuous
How Much Time from Moment to A Point In The Past	Past Perfect
Finished Time Word	Past Simple
Process Duration To A Point In The Past	Past Perfect Continuous
Process Duration Till Now	Present Perfect Continuous
Overlapping Action	Past Continuous
Result At A Time In The Past	Past Perfect Continuous
Annoying Habits	Present Continuous
News / Recent Events	Present Perfect
Habits	Present Simple
Present Result Of A Process	Present Perfect Continuous
Life Experience	Present Perfect
Unfinished Time Word	Present Perfect
Action Finished Before Another Past Action	Past Perfect
Temporary Situations (акцент на Now)	Present Continuous
Definite Future Plans	Present Continuous
Always Truth	Present Simple
Temporary Situations (акцент на прошлом)	Present Perfect Continuous
Present Result Of An Action	Present Perfect
Some Past Habits	Past Continuous
Unreal / Imaginary Things	Past Simple
Future In Time Clauses	Present Simple'''

        data = data.split('\n')

        quizlist = []

        tenses = [
            'Past Simple',
            'Past Continuous',
            'Past Perfect',
            'Past Perfect Continuous',
            'Present Simple',
            'Present Continuous',
            'Present Perfect',
            'Present Perfect Continuous',
        ]

        random.shuffle(data)

        for i, line in enumerate(data):
            example, tense = line.split('\t')

            options = list(set(tenses))
            options.remove(tense)

            options = random.sample(options, 4)
            options.append(tense)
            random.shuffle(options)

            quizlist.append({
                'word': {
                    'definitions': [],
                    'spelling': example,
                    'transcription': '',
                    'pronunciation': '',
                },
                'word_id': i,
                'definition_id': i,
                'quiz': example,
                'options': options,
                'answer': options.index(tense),
            })

        data = {
            'results': quizlist,
        }

        return HttpResponse(
            json.dumps(data, ensure_ascii=False),
            status=200,
            content_type='application/json; charset=utf-8')


class Test2APIView(APIView):

    def get(self, request, id, format=None):
        # статусы, подходящие для этого теста
        # statuses = [
        #     Word.Status.Rotation.value,
        #     Word.Status.Studying.value,
        # ]
        words_to_test = Word.objects.filter(list__id=id).order_by('?')
        # all_words = Word.objects.all().exclude(part_of_speech='phrasal_verb').order_by('?').values_list('spelling', flat=True)[:300]

        quizlist = []

        for word in words_to_test:
            definitions = word.definitions.all().order_by('?')
            if not definitions:
                continue

            # одно случайное определение
            definition = definitions[0]
            answer = definition.spelling

            options = Word.objects.all().order_by('?')

            # совпадение части речи
            if word.part_of_speech:
                options = options.filter(part_of_speech=word.part_of_speech)
            else:
                options = options.exclude(part_of_speech='phrasal_verb')

            def distance(el):
                # res = jellyfish.jaro_distance(word.spelling, el.spelling)
                # res = jellyfish.levenshtein_distance(word.spelling, el.spelling)
                res = jellyfish.damerau_levenshtein_distance(word.spelling, el.spelling)
                return res

            options_by_distance = sorted(list(options[:500]), reverse=False, key=distance)

            # print()
            # print(word.spelling)
            # for o in options_by_distance[:30]:
            #     print(o.spelling)

            # print('\n\n\n')
            # print(word)
            # print(len(options), word.part_of_speech)
            # print(options_by_distance)

            # фильтр на абсолютное совпадение и еще что-нибудь
            final_options_texts = []
            for o in options_by_distance:
                if o.spelling != answer and (len(answer) < 4 or (answer not in o.spelling)):
                    final_options_texts.append(o.spelling)

            # только уникальные слова
            final_options_texts = list(set(final_options_texts))

            try:
                final_options_texts = random.sample(final_options_texts[:10], 4)
            except ValueError:
                pass

            final_options_texts.append(answer)
            random.shuffle(final_options_texts)

            pronunciation = word.pronunciations.first()
            if pronunciation:
                pronunciation_url = pronunciation.audio.url
            else:
                pronunciation_url = None

            quizlist.append({
                'word': WordSerializer(word).data,
                'word_id': word.id,
                'definition_id': definition.id,
                'quiz': definition.translation or definition.interpretation,
                'options': final_options_texts,
                'answer': final_options_texts.index(answer),
                'pronunciation': pronunciation_url,
            })

        data = {
            'results': quizlist,
        }

        return HttpResponse(
            json.dumps(data, ensure_ascii=False),
            status=200,
            content_type='application/json; charset=utf-8')


class TestPhrasalAPIView(APIView):

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

    def get(self, request, id, format=None):
        # статусы, подходящие для этого теста
        # statuses = [
        #     Word.Status.Rotation.value,
        #     Word.Status.Studying.value,
        # ]
        words_to_test = Word.objects.filter(list__id=id).order_by('?')

        quizlist = []

        all_verbs = []
        all_adverb_particle = []
        all_prepositions = SOME_PREPS
        for w in Word.objects.filter(list__id=id).order_by('?')[:50]:
            verb = w.spelling.split(' ')[0]
            try:
                adverb_particle = w.spelling.split(' ')[1]
            except:
                adverb_particle = w.spelling
            all_verbs.append(verb)
            all_adverb_particle = all_adverb_particle + adverb_particle.split('/')

        all_verbs = list(set(all_verbs))
        all_adverb_particle = list(set(all_adverb_particle))

        for word in words_to_test:
            definitions = word.definitions.all().order_by('?')
            if not definitions:
                continue

            # одно случайное определение
            definition = definitions[0]
            answer = definition.spelling

            # случайный пример
            e = definition.examples.order_by('?').first()
            if not e:
                continue

            quiz_text = ' ' + e.text
            # quiz_text = quiz_text.replace(' ' + adverb_particle, ' __%s__' % adverb_particle)

            if word.part_of_speech == Word.Pos.Phrasal_verb.value:

                verb = word.spelling.split(' ')[0]
                adverb_particle = word.spelling.split(' ')[1]

                try:
                    preposition = word.spelling.split(' ')[2]
                except IndexError:
                    preposition = None

                # quiz_text = quiz_text.replace(' ' + adverb_particle, ' ____')
                adverb_particle_used = ''
                for ap in adverb_particle.split('/'):
                    if ap in quiz_text:
                        quiz_text = quiz_text.replace(' ' + ap, ' ____')
                        adverb_particle_used = ap
                        break

                quiz_text = quiz_text.lstrip(' ')

                res = self.find_by_distance(verb, quiz_text)

                if res:
                    if verb in quiz_text.lower():
                        # logger.debug('\n' + e_text.replace(res, '__%s__' % res))
                        quiz_text = quiz_text.replace(res, '____')
                    else:
                        # logger.warning('\n' + e_text.replace(res, '__%s__' % res))
                        quiz_text = quiz_text.replace(res, '____')
                else:
                    logger.error('err: %s \t %s' % (verb, quiz_text))
                    continue

                if preposition:
                    quiz_text = quiz_text.replace('____ %s' % preposition, '____ ____')

                # варианты ответов
                random.shuffle(all_verbs)
                random.shuffle(all_adverb_particle)
                random.shuffle(all_prepositions)

                v_options = ([verb] + list(set(all_verbs) - {verb}))[:5]
                p_options = ([adverb_particle_used] + list(set(all_adverb_particle) - {adverb_particle_used}))[:5]

                random.shuffle(v_options)
                random.shuffle(p_options)

                options_set = [
                    {
                        'options': v_options,
                        'answer': v_options.index(verb)
                    }, {
                        'options': p_options,
                        'answer': p_options.index(adverb_particle_used)
                    },
                ]

                # если дали еще и предлог
                if preposition:
                    pp_options = ([preposition] + list(set(all_prepositions) - {preposition}))[:5]
                    random.shuffle(pp_options)
                    options_set.append({
                        'options': pp_options,
                        'answer': pp_options.index(preposition)
                    })

            else:
                ###############################
                # словосочетания с предлогами #
                ###############################

                item = ' '.join(definition.spelling.split(' ')[:-1])  # всё, кроме последнего куска
                preposition = ' '.join(definition.spelling.split(' ')[-1:])  # последний кусок

                res = self.find_by_distance(item, quiz_text)

                if res:
                    head, sep, tail = quiz_text.partition(res)
                    tail = tail.replace(preposition, '____', 1)
                    quiz_text = head + sep + tail
                else:
                    quiz_text = quiz_text.replace(preposition, '____', 1)

                quiz_text = quiz_text.strip()

                pp_options = ([preposition] + list(set(all_prepositions) - {preposition}))[:5]
                random.shuffle(pp_options)

                options_set = [
                    {
                        'options': pp_options,
                        'answer': pp_options.index(preposition)
                    }
                ]

            quizlist.append({
                'word': WordSerializer(word).data,
                'word_id': word.id,
                'definition_id': definition.id,
                'quiz': quiz_text,
                'quiz_answer': e.text,
                'quiz_hint': definition.translation or definition.interpretation,
                'options_set': options_set,
            })

        data = {
            'results': quizlist[:10],
        }

        return HttpResponse(
            json.dumps(data, ensure_ascii=False),
            status=200,
            content_type='application/json; charset=utf-8')


class AttemptAPIView(APIView):

    def post(self, request, format=None):

        data = dict(request.data)

        if request.user.is_authenticated:
            # добавить юзера к данным
            data['user'] = request.user.pk
        else:
            # ничего не делать
            return Response({}, status=200)

        serializer = AttemptSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            # if 'word' in request.data:
            #
            #     # запись результата в поля слова
            #     word_id = serializer.data['word']
            #     word = Word.objects.get(id=word_id)
            #
            #     if serializer.data['result'] == 'success':
            #         word.success_cnt += 1
            #     else:
            #         word.error_cnt += 1
            #
            #     if word.status in [Word.Status.New.value, Word.Status.Rotation.value]:
            #         if word.success_cnt > 0 or word.error_cnt > 0:
            #             word.status = Word.Status.Studying.value
            #
            #     if word.status == Word.Status.Studying.value and word.score >= 5:
            #         word.status = Word.Status.Level1.value
            #
            #     word.save()
            #
            # elif 'sentence' in request.data:
            #
            #     # запись результата в поля предложения
            #     sentence_id = serializer.data['sentence']
            #     sentence = Sentence.objects.get(id=sentence_id)
            #
            #     if serializer.data['result'] == 'success':
            #         sentence.success_cnt += 1
            #     else:
            #         sentence.error_cnt += 1
            #
            #     sentence.save()
            #
            # else:
            #     print('xxx', serializer.data)

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


def replace_spaces(match):
    return '[' + match.group(1).replace(' ', ' ') + '](' + match.group(2).replace(' ', ' ') + ')'


def sentence_converter(s):
    return re.sub(r'\[(.*?)\]\s*\((.*?)\)', replace_spaces, s)


def sentence_task(request):

    # выбирается случайная запись из 20% наименее изученных
    cnt = Sentence.objects.count()
    cnt = min(cnt/5, 30)
    sents = Sentence.objects.filter(is_hidden=False).order_by('success_cnt', 'error_cnt')[:cnt]
    sent = random.choice(sents)

    text = sentence_converter(sent.text)
    text = text.replace(' [', ' [')

    # text = '[Have you ever been](you ever be) here? Yes, I [was](be) here on holiday last year.'

    words = []
    for lemma in text.split(' '):
        if lemma and lemma[0] == '[':
            lemma = lemma.strip('[').strip(')').strip()
            answer, hint = lemma.split('](')
            answers = list(map(lambda s: s.replace(' ', ' ').lower().strip(), answer.split('/')))
            words.append({
                'hint': hint,
                'answers': answers,
                'source': answers[0],
            })
        else:
            words.append({
                'text': lemma,
            })

    res = {
        'id': sent.id,
        'is_flaged': sent.is_flaged,
        # 'success_cnt': sent.success_cnt,
        # 'error_cnt': sent.error_cnt,
        'text': sent.text,
        'words': words,
    }

    return HttpResponse(
        json.dumps(res, ensure_ascii=False),
        status=200,
        content_type='application/json; charset=utf-8')


def sentence_status(request):
    """
    Действия с предложениями
    """
    sentence_id = request.POST.get('sentence_id')
    action = request.POST.get('action')

    sentence = Sentence.objects.get(id=sentence_id)

    if action == 'hide':
        sentence.is_hidden = True

    if action == 'flag':
        sentence.is_flaged = True

    if action == '-hide':
        sentence.is_hidden = False

    if action == '-flag':
        sentence.is_flaged = False

    sentence.save()

    return HttpResponse(
        json.dumps({'status': 'ok'}, ensure_ascii=False),
        status=200,
        content_type='application/json; charset=utf-8'
    )
