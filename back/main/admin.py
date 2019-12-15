import logging
from admin_decorators import boolean
from django.contrib.admin import ModelAdmin, StackedInline
from django.db.models import Count, Max
from main.models import List, Word, Definition, Pronunciation, Example, Attempt, Sentence
from project.admin import custom_admin_site
from django.contrib import admin

logger = logging.getLogger(__name__)


@admin.register(List, site=custom_admin_site)
class ListAdmin(ModelAdmin):
    list_display = ['name', 'owner', 'sharable', 'created_at']
    fields = ['name', 'owner', 'sharable']
    readonly_fields = ['owner']
    list_filter = ['sharable']


class DefinitionInline(StackedInline):
    model = Definition
    list_display = ['spelling', 'interpretation', 'translation']
    extra = 0


@admin.register(Word, site=custom_admin_site)
class WordAdmin(ModelAdmin):
    list_display = ['spelling', 'part_of_speech', 'zipf', 'is_hidden',
                    'has_audio', 'has_example', 'example', 'short_mean', 'syn_string']
    list_filter = ['list', 'part_of_speech']
    search_fields = ['spelling', 'short_mean', 'syn_string']
    actions_on_top = False
    actions_on_bottom = True

    inlines = [DefinitionInline]

    @boolean
    def has_audio(self, obj):
        return obj.pronunciations.count() > 0

    @boolean
    def has_example(self, obj):
        for d in obj.definitions.all():
            if d.examples.count() > 0:
                return True
        return False

    def example(self, obj):
        for d in obj.definitions.all():
            return d.examples.first()


@admin.register(Sentence, site=custom_admin_site)
class SentenceAdmin(ModelAdmin):
    list_display = ['id', 'text', 'is_hidden', 'is_flaged']
    list_filter = ['list', 'is_hidden', 'is_flaged']
    search_fields = ['text']
    actions_on_top = False
    actions_on_bottom = True


@admin.register(Pronunciation, site=custom_admin_site)
class PronunciationAdmin(ModelAdmin):
    pass


@admin.register(Example, site=custom_admin_site)
class ExampleAdmin(ModelAdmin):
    list_display = ['definition', 'text', 'description']
    search_fields = ['text', 'description']
    actions_on_top = False
    actions_on_bottom = True


@admin.register(Attempt, site=custom_admin_site)
class AttemptAdmin(ModelAdmin):
    list_display = ['created_at', 'word', 'sentence', 'answer', 'definition', 'test', 'result',]
    list_filter = ['result', 'created_at']
    readonly_fields = ['user', 'word', 'definition', 'sentence']


class ExampleInline(StackedInline):
    model = Example
    list_display = ['text', 'description']
    extra = 0


class ItemCountListFilter(admin.SimpleListFilter):
    title = 'examples count'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'count'

    def lookups(self, request, model_admin):
        max_value = Definition.objects.all().annotate(
            count_items=Count('examples')
        ).aggregate(max_value=Max('count_items'))['max_value']
        return [(i, i) for i in range(0, max_value)]

    def queryset(self, request, queryset):
        val = self.value()
        if val is not None:
            return queryset.annotate(count_items=Count('examples')).filter(count_items=self.value())
        else:
            return queryset


@admin.register(Definition, site=custom_admin_site)
class DefinitionAdmin(ModelAdmin):
    list_display = ['word', 'spelling', 'interpretation', 'translation', 'level', 'has_example']
    list_select_related = ['word']
    list_filter = ['word__list', 'level', ItemCountListFilter]
    list_editable = ['spelling', 'interpretation', 'translation']
    search_fields = ['spelling', 'interpretation', 'translation', 'context']
    readonly_fields = ['word']
    inlines = [ExampleInline]
    actions_on_top = False
    actions_on_bottom = True

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #     return qs.annotate(num_examples=Count('examples'))

    @boolean
    def has_example(self, obj):
        if obj.examples.count() > 0:
            return True
        return False

    # def get_num_examples(self, obj):
    #     return obj.num_examples
