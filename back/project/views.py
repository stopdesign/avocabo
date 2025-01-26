from django.views.generic import TemplateView


class AccessDeniedView(TemplateView):
    template_name_desktop = "403.html"
    template_name_mobile = "403.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=403)


class PageNotFoundView(TemplateView):
    template_name_desktop = "desktop/errors/404.mako"
    template_name_mobile = "mobile/errors/404.mako"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=404)


class ServerErrorView(TemplateView):
    template_name_desktop = "500.html"
    template_name_mobile = "500.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context, status=500)


def server_error_emulate(request, exception=None):
    return 1 / 0
