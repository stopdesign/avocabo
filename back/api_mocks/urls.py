from django.urls import path

from . import views

app_name = "api_mocks"

urlpatterns = [
    path("api/settings/email/", views.mock_settings_email, name="settings_email"),
    path(
        "api/settings/delete-account/",
        views.mock_settings_delete_account,
        name="settings_delete_account",
    ),
]
