from django.urls import path

from main.views import auth, pages

app_name = "main"

urlpatterns = [
    path("", pages.index, name="index"),
    path("list/<int:list_id>/", pages.words, name="index"),
    path("api/list/", pages.ListAPIListView.as_view()),
    path("api/user_list/", pages.UserListAPIView.as_view()),
    path("api/hide_word/", pages.HideWordAPIView.as_view()),
    path("api/list/<int:id>/", pages.ListAPIView.as_view()),
    path("api/list/<int:id>/test1/", pages.Test1APIView.as_view()),
    path("api/list/<int:id>/test_phrasal/", pages.TestPhrasalAPIView.as_view()),
    path("api/test_tenses/", pages.TestTensesAPIView.as_view()),
    path("api/stat/", pages.StatAPIView.as_view()),
    # path('api/rotation/', pages.RotationAPIListView.as_view()),
    path("api/sentence/", pages.sentence_task),
    path("api/sentence_status/", pages.sentence_status),
    path("api/attempt/", pages.AttemptAPIView.as_view()),
    path("api/word/<int:id>/", pages.WordAPIView.as_view()),
    # auth-test
    path("api/auth/test/", auth.test),
]
