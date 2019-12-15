from django.views.generic import TemplateView


class CacheMixin:
    cache_max_age = 60

    def render_to_response(self, *args, **kwargs):
        response = super(CacheMixin, self).render_to_response(*args, **kwargs)
        if isinstance(self.cache_max_age, int):
            response['Cache-Control'] = 'private, max-age=%s' % self.cache_max_age
            response['X-Accel-Expires'] = self.cache_max_age
        return response


class CachedTemplateView(CacheMixin, TemplateView):
    pass
