from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.urls import include, path, re_path
from django.views.static import serve as django_serve
from main.views.auth import RegisterView

from project.admin import custom_admin_site
from project.views import (
    AccessDeniedView,
    PageNotFoundView,
    ServerErrorView,
    server_error_emulate,
)

app_name = "project"

admin.site = custom_admin_site
admin.autodiscover()

urlpatterns = [
    # Your main app
    path("", include(("main.urls", "main"), namespace="main")),
    # Rest-auth endpoints
    path("api/rest-auth/", include("dj_rest_auth.urls")),
    path("api/rest-auth/registration/", RegisterView.as_view(), name="rest_register"),
    # Password-reset stuff
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # Admin site
    path("admin/", admin.site.urls),
    # Emulate server error
    path("500-e/", server_error_emulate, name="server_error_emulate"),
]

# Favicon & media
urlpatterns += [
    re_path(r"^(?P<path>favicon\.ico)$", staticfiles_serve, name="favicon"),
    re_path(r"^media/(?P<path>.*)$", django_serve, {"document_root": settings.MEDIA_ROOT}, name="media"),
]

# Debug-only “fun”
if settings.DEBUG:
    urlpatterns += [
        path("403/", AccessDeniedView.as_view(), name="403"),
        path("404/", PageNotFoundView.as_view(), name="404"),
        path("500/", ServerErrorView.as_view(), name="500"),
        re_path(r"^static/(?P<path>.*)$", staticfiles_serve),
    ]

# Custom error handlers
handler403 = AccessDeniedView.as_view()
handler404 = PageNotFoundView.as_view()
# handler500 = ServerErrorView.as_view()

# Pretty name for the “main” app
apps.get_app_config("main").verbose_name = "Words App"
