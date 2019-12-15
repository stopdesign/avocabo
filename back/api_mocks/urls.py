from django.conf.urls import url

from . import views

app_name = 'api_mocks'

urlpatterns = [
    url(r"^api/settings/email/$", view=views.mock_settings_email, name='settings_email'),
    url(r"^api/settings/delete-account/$", view=views.mock_settings_delete_account, name='settings_delete_account')
]
