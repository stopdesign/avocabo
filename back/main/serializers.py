import logging

from django.db.models import Count
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from main.models import List, Word, Definition, Example, Pronunciation, Attempt, UserList, UserWord

logger = logging.getLogger(__name__)


class PronunciationSerializer(ModelSerializer):

    class Meta:
        model = Pronunciation
        fields = ['id', 'audio', 'description']


class ExampleSerializer(ModelSerializer):

    class Meta:
        model = Example
        fields = ['id', 'text']


class DefinitionSerializer(ModelSerializer):
    # pronunciations = PronunciationSerializer(many=True, read_only=True)
    examples = ExampleSerializer(many=True, read_only=True)

    class Meta:
        model = Definition
        fields = ['id', 'spelling', 'interpretation', 'translation', 'level', 'context', 'note', 'examples']


class WordSerializer(ModelSerializer):
    # definitions = DefinitionSerializer(many=True, read_only=True)
    score = SerializerMethodField()
    definitions = SerializerMethodField()
    pronunciation = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        """
        Юзер нужен для подсчета количества ответов по данному слову
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_score(self, obj):
        if (self.user is None) or not self.user.is_authenticated:
            score = 0
        else:
            all_res = str(list(Attempt.objects.filter(user_id=self.user.pk, word_id=obj.id).values_list('result', flat=True)))
            success_cnt = all_res.count("'success'")
            error_cnt = all_res.count("'error'")

            # TODO: придумать, куда положить скорринг и его правила
            score = min(9, max(0, success_cnt - error_cnt * 2))
        return score

    def get_pronunciation(self, obj):
        pronunciation = obj.pronunciations.order_by('-description').first()
        if pronunciation:
            return pronunciation.audio.url
        return None

    def get_definitions(self, obj):
        qs = obj.definitions.all()
        leveled_count = 0
        # all_count = qs.count()
        for d in qs:
            if d.level:
                leveled_count += 1
        if leveled_count > 3:
            qs = obj.definitions.exclude(level='').exclude(level=None)
        if leveled_count == 0:
            qs = qs[:3]
        else:
            qs = qs[:5]
        return DefinitionSerializer(qs, many=True).data

    class Meta:
        model = Word
        fields = ['id', 'spelling', 'is_hidden', 'definitions', 'pronunciation',
                  'transcription', 'part_of_speech', 'zipf', 'score']


class ListSerializer(ModelSerializer):
    count = SerializerMethodField()
    hidden = SerializerMethodField()
    new_count = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def get_count(self, obj):
        if self.user and self.user.is_authenticated:
            hidden_word_ids = UserWord.objects.filter(user_id=self.user.pk, word__list=obj).values('word_id')
            cnt = Word.objects.filter(list=obj).exclude(id__in=hidden_word_ids).count()
            return cnt
        return obj.words.count()

    def get_hidden(self, obj):
        if self.user and self.user.is_authenticated:
            try:
                ul = UserList.objects.get(user=self.user, list=obj)
                return ul.hidden
            except UserList.DoesNotExist:
                pass
        return False

    def get_new_count(self, obj):
        if self.user and self.user.is_authenticated:
            hidden_word_ids = UserWord.objects.filter(user_id=self.user.pk, word__list=obj).values('word_id')

            new = Word.objects.filter(list=obj)
            new = new.exclude(id__in=hidden_word_ids)
            new = new.annotate(attempts_cnt=Count('attempts'))
            new_cnt = new.filter(attempts_cnt=0).count()
            return new_cnt
        return None

    class Meta:
        model = List
        fields = ['id', 'name', 'count', 'new_count', 'hidden']


class UserListSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)
    list = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserList
        fields = ['user', 'list', 'hidden']


class UserWordSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)
    word = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserList
        fields = ['user', 'word', 'hidden']


class ListDetailsSerializer(ModelSerializer):
    # words = WordSerializer(many=True, read_only=True)
    words = SerializerMethodField()

    def __init__(self, *args, **kwargs):
        """
        Юзер нужен для подсчета количества ответов по данному слову
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def get_words(self, obj):
        qs = obj.words.filter()

        # отфильтровать те, которые выключены
        if self.user and self.user.is_authenticated:
            # все слова данного списка, которые выключены у юзера
            hidden_word_ids = UserWord.objects.filter(user=self.user).values('word_id')
            qs = qs.exclude(id__in=hidden_word_ids)

        return WordSerializer(qs[:200], user=self.user, many=True).data

    class Meta:
        model = List
        fields = ['id', 'name', 'words']


class AttemptSerializer(ModelSerializer):

    class Meta:
        model = Attempt
        fields = '__all__'
