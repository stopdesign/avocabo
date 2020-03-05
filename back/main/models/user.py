import uuid
import hashlib
import logging
from datetime import datetime
from django.db.models import Q
from pytz import utc
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, UserManager

logger = logging.getLogger(__name__)


def uuid4_hex():
    return uuid.uuid4().hex


class UserModelManager(UserManager):
    """
    Регистронезависимый поиск и валидация юзера (username и email)
    """
    def filter(self, **kwargs):
        if 'username' in kwargs:
            kwargs['username__iexact'] = kwargs['username']
            del kwargs['username']
        if 'email' in kwargs:
            kwargs['email__iexact'] = kwargs['email']
            del kwargs['email']
        return super(UserModelManager, self).filter(**kwargs)

    def get(self, **kwargs):
        if 'username' in kwargs:
            kwargs['username__iexact'] = kwargs['username']
            del kwargs['username']
        if 'email' in kwargs:
            kwargs['email__iexact'] = kwargs['email']
            del kwargs['email']
        return super(UserModelManager, self).get(**kwargs)

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=False,
        blank=False,
        default=uuid4_hex,
        help_text=_('Required.'),
        error_messages={
            'unique': _("A user with that UID already exists."),
        }
    )
    password_changed_at = models.DateTimeField(null=True, blank=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserModelManager()

    # это подписки на темы
    subscriptions = models.ManyToManyField('List', related_name='user_set', blank=True)

    # слова в ротации, id через пробел
    rotation = models.TextField(max_length=1000, null=False, default='', blank=True)

    @property
    def rotation_count(self):
        """
        Целевое количество слов в ротации.
        """
        return 20

    @property
    def user_subscriptions(self):
        from main.models import List
        if self.pk:
            subscriptions = self.subscriptions.all().values_list('id', flat=True)
            items = List.objects.filter(Q(owner=self) | Q(sharable=True) | Q(id__in=subscriptions))
        else:
            items = List.objects.filter(sharable=True)
        return items

    def __str__(self):
        return self.email

    def get_signed_hash(self):
        signed_str = '%d_%s' % (self.id, hashlib.md5(settings.SECRET_KEY.encode('utf-8')).hexdigest())
        return hashlib.sha256(signed_str.encode('utf-8')).hexdigest()[:16]

    def set_password(self, *args, **kwargs):
        """
        Фиксация момента смены пароля.
        """
        super().set_password(*args, **kwargs)
        self.password_changed_at = datetime.utcnow().replace(tzinfo=utc)

    def update_rotation(self):
        """
        Обновляет список слов в ротации.
        Из списка удаляются изученные слова, в список добавляются
        """

        """
        1. Разобрать строку ротации на список.
        
        2. Проверить статус каждого слова и оставить только актуальные:
            — cписок активен
            — пользователь на него подписан
        
        3. Проверить количество слов (и сократить список до него).
        
        4. Если список меньше целевой длины, добавить нужное количество других слов.
        
        5. Сдампить и сохранить новую ротацию.
        """
        from main.models import Word, Attempt

        rotation = self.rotation.strip().split(' ')
        rotation = filter(None, rotation)
        rotation = [int(r) for r in rotation]

        new_r_words = []

        # выключенные листы
        hidden_lists = self.user_lists.filter(hidden=True).values_list('list_id', flat=True)

        # id активных подписок пользователя
        list_ids = self.user_subscriptions.exclude(id__in=hidden_lists).values_list('id', flat=True)

        # фильтр по активным группам пользователя
        words = Word.objects.filter(list__in=list_ids, id__in=rotation).exclude(definitions=None).values_list('id', flat=True)

        # все слова, которые потенциально можно добавить
        words_count = Word.objects.filter(list__in=list_ids).exclude(definitions=None).count()

        # выбрать все попытки по словам из ротации
        attempts = list(Attempt.objects.filter(user_id=self.pk, word_id__in=words).values('user', 'word', 'result'))

        # группировать по id

        # print('\n')
        # print(attempts)

        attempts_by_word_id = {}
        for attempt in attempts:
            attempts_by_word_id.setdefault(attempt['word'], []).append(attempt)

        # print('attempts_by_word_id', attempts_by_word_id)

        # Пересечение список с сохранением порядка первого списка.
        # Это слова, которые сейчас есть в ротации и существуют в подписках
        words = [value for value in rotation if value in words]

        for r_word in words:
            all_res = str(attempts_by_word_id.get(r_word, ''))

            success_cnt = all_res.count("'success'")
            error_cnt = all_res.count("'error'")

            # TODO: придумать, куда положить скорринг и его правила
            score = min(10, max(0, success_cnt - error_cnt * 2))

            if score < 5:
                new_r_words.append(r_word)

        # print('words_count', words_count)
        # print('new_r_words 1', new_r_words)

        new_r_words = new_r_words[:self.rotation_count]

        # Cколько слов нужно добавить
        to_add = self.rotation_count - len(new_r_words)
        to_add = min(to_add, words_count)

        # print('to_add', to_add)

        if to_add > 0:
            print('нужно добавить', to_add)

            # TODO: тут важно сначала обработать слова, которые уже когда-то были в ротации, но еще не доделаны
            # TODO: и не находятся в ротации сейчас
            words = Word.objects.filter(list__in=list_ids).exclude(definitions=None).exclude(id__in=new_r_words)
            words = words.values_list('id', flat=True).order_by('?')

            # print('words_2 ===', len(words))

            # выбрать все попытки по словам из ротации
            attempts = list(Attempt.objects.filter(user_id=self.pk, word_id__in=words).values('user', 'word', 'result'))

            attempts_by_word_id = {}
            for attempt in attempts:
                attempts_by_word_id.setdefault(attempt['word'], []).append(attempt)

            for r_word in words:
                all_res = str(attempts_by_word_id.get(r_word, ''))

                success_cnt = all_res.count("'success'")
                error_cnt = all_res.count("'error'")

                # TODO: придумать, куда положить скорринг и его правила
                score = min(10, max(0, success_cnt - error_cnt * 2))

                if score < 5:
                    new_r_words.append(r_word)

                if len(new_r_words) >= self.rotation_count:
                    break

        words_dump = ' '.join(['%s' % w for w in new_r_words])

        # print('\nnew_r_word_2', len(new_r_words), words_dump)

        # print()
        # print()

        if self.rotation != words_dump and self.pk:
            self.rotation = words_dump
            self.save(update_fields=['rotation'])

    class Meta:
        db_table = 'auth_user'
        permissions = (
            # всякие кастомные права
            # ("can_view_dashboard", "Can view dashboard"),
        )
