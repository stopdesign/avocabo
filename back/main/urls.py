from django.conf.urls import url
from main.views import pages, auth

app_name = 'main'

urlpatterns = [
    url(r'^$', view=pages.index, name='index'),
    url(r'^list/(?P<list_id>[0-9]+)/$', view=pages.words, name='index'),

    url(r'^api/list/(?P<id>[0-9]+)/$', pages.ListAPIView.as_view()),
    url(r'^api/list/(?P<id>[0-9]+)/test1/$', pages.Test1APIView.as_view()),
    url(r'^api/list/(?P<id>[0-9]+)/test_phrasal/$', pages.TestPhrasalAPIView.as_view()),
    url(r'^api/list/$', pages.ListAPIListView.as_view()),
    url(r'^api/test_tenses/$', pages.TestTensesAPIView.as_view()),

    # url(r'^api/rotation/$', pages.RotationAPIListView.as_view()),

    url(r'^api/sentence/$', pages.sentence_task),
    url(r'^api/sentence_status/$', pages.sentence_status),

    url(r'^api/attempt/$', pages.AttemptAPIView.as_view()),

    url(r'^api/word/(?P<id>[0-9]+)/$', pages.WordAPIView.as_view()),

    # auth-test
    url('^api/auth/test/$', auth.test),
]
