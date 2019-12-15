import sys
import logging
from django.core.management.color import color_style


class StdoutHandler(logging.StreamHandler):

    def __init__(self, stream=None):
        super(StdoutHandler, self).__init__(stream or sys.stdout)


class DjangoColorsFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(DjangoColorsFormatter, self).__init__(style='{', *args, **kwargs)
        self.style = self.configure_style(color_style())

    def configure_style(self, style):
        style.DEBUG = style.HTTP_NOT_MODIFIED
        style.INFO = style.HTTP_SUCCESS
        style.WARNING = style.HTTP_NOT_FOUND
        style.ERROR = style.ERROR
        style.CRITICAL = style.HTTP_SERVER_ERROR
        return style

    def format(self, record):
        message = super(DjangoColorsFormatter, self).format(record)
        colorizer = getattr(self.style, record.levelname, self.style.HTTP_SUCCESS)

        # print('record', type(record))
        # print('record', type(record))

        # немного сокращаю название модуля
        if '.management.commands.' in record.name:
            message = message.replace(str(record.name), str(record.module))

        res = colorizer(message)

        # # traceback для серьезных ошибок
        # if record.levelname in ['ERROR', 'CRITICAL']:
        #     exc_info = sys.exc_info()
        #     if exc_info:
        #         res += '\n' + self.formatException(exc_info)

        return res
