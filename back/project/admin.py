import logging
from django.contrib.admin import AdminSite, StackedInline
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from constance.admin import Config, ConstanceAdmin
from logentry_admin.admin import LogEntryAdmin

logger = logging.getLogger(__name__)


class CustomizedAdminSite(AdminSite):
    site_header = 'OCS Demo'
    site_title = 'R&D Lab'
    index_title = 'Admin'
    empty_value_display = '¯\_(ツ)_/¯'

    def index(self, request, extra_context=None):
        """
        Можно просунуть дополнительный контент для главной страницы админки
        """
        if extra_context is None:
            extra_context = {}

        extra_context.update({
            # 'stats': stats,
        })

        return super(CustomizedAdminSite, self).index(request, extra_context)


custom_admin_site = CustomizedAdminSite()


user_model = get_user_model()


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        # ('Permissions', {
        #     'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        # }),
        # ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Subscriptions', {'fields': ('subscriptions', 'rotation')}),
    )
    readonly_fields = ['username', 'rotation']
    filter_horizontal = ('groups', 'user_permissions', 'subscriptions')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


custom_admin_site.register(user_model, CustomUserAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register([Config], ConstanceAdmin)
custom_admin_site.register(LogEntry, LogEntryAdmin)
