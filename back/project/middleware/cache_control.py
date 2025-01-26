from django.conf import settings
from django.utils.cache import get_max_age
from django.utils.deprecation import MiddlewareMixin


DEFAULT_MAX_AGE = 0


class DefaultCacheHeaders(MiddlewareMixin):
    """
    Проброс времени из Cache-Control в X-Accel-Expires.
    Установка заголовков против кэширования по умолчанию.
    """

    def process_response(self, request, response):
        path = request.get_full_path()

        # для статики ничего не менять
        if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
            return response

        if response.has_header("Cache-Control"):
            # заголовок уже поставлен бэкендом, сохраняю и добавляю X-Accel-Expires на то же время
            max_age = get_max_age(response)
            response["X-Accel-Expires"] = max_age or 0
        else:
            # заголовка нет, ставлю значение по умолчанию
            response["Cache-Control"] = "private, max-age=%s, no-cache, no-store, must-revalidate" % DEFAULT_MAX_AGE
            response["X-Accel-Expires"] = "%s" % DEFAULT_MAX_AGE

        return response
