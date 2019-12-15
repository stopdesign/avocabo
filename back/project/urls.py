from django.apps import apps
from django.conf import settings
from django.conf.urls import url, include
from django.views.static import serve
from django.urls import re_path
from django.contrib import admin

from main.views.auth import RegisterView
from project.admin import custom_admin_site
from django.contrib.staticfiles.views import serve as staticfiles_serve
from project.views import server_error_emulate
from project.views import AccessDeniedView, PageNotFoundView, ServerErrorView


app_name = 'project'

admin.site = custom_admin_site
admin.autodiscover()


from django.contrib.auth import views


urlpatterns = [

    # приложение
    url(r'', include('main.urls', namespace='main')),

    # API аутентификации и регистрации
    url(r'^api/rest-auth/', include('rest_auth.urls')),
    url(r'^api/rest-auth/registration/$', RegisterView.as_view(), name='rest_register'),

    # обработка сброса пароля
    url(r'^password_reset/$', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done/$', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done/$', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # админка
    url(r'^admin/', admin.site.urls),

    # эмуляция ошибки (должно работать и без DEBUG)
    url(r'^500-e/$', server_error_emulate),

]

# запись для media нужна для работы reverse
urlpatterns += [
    url(r'^(?P<path>favicon\.ico)$', staticfiles_serve, name='favicon'),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
]

# просмотр служебных страниц в режиме отладки
if settings.DEBUG:
    urlpatterns += [
        url(r'^403/$', AccessDeniedView.as_view()),
        url(r'^404/$', PageNotFoundView.as_view()),
        url(r'^500/$', ServerErrorView.as_view()),
    ]
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', staticfiles_serve),
    ]

# обработчики служебных страниц
handler403 = AccessDeniedView.as_view()
handler404 = PageNotFoundView.as_view()
# handler500 = ServerErrorView.as_view()


# приличное имя для некоторых приложений
apps.get_app_config('main').verbose_name = 'Words App'
