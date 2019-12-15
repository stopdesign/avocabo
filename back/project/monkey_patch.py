import logging
from decimal import Decimal
from django.core.management.commands.runserver import Command as RunserverCommand
from django.contrib.staticfiles.management.commands.runserver import Command
from django.forms import NumberInput
# from django_cron import CronJobManager, get_current_time


###
# Патчим поле NumberInput, чтобы не было проблем с Scientific Notation у малых значений Decimal.
# Заодно выключаются всякие там стрелочки внутри полей с числами.

def format_value(self, value):
    if value == '' or value is None:
        return None
    if isinstance(value, Decimal):
        return '{:f}'.format(value)
    else:
        return str(value)


NumberInput.format_value = format_value
NumberInput.input_type = 'text'


###
# Патч для вывода traceroute и другого результата работы заданий django_cron в консоль.

# def make_log(self, *messages, **kwargs):
#     cron_log = self.cron_log
#
#     cron_job = getattr(self, 'cron_job', self.cron_job_class)
#     cron_log.code = cron_job.code
#
#     cron_log.is_success = kwargs.get('success', True)
#     cron_log.message = self.make_log_msg(*messages)
#     cron_log.ran_at_time = getattr(self, 'user_time', None)
#     cron_log.end_time = get_current_time()
#     cron_log.save()
#
#     logger = logging.getLogger('runcrons_console')
#     if cron_log.is_success:
#         for msg in messages:
#             if msg:
#                 logger.debug(msg)
#     else:
#         for msg in messages:
#             if msg:
#                 logger.warning(msg)
#
#
# CronJobManager.make_log = make_log


# Выключаю стандартный StaticFilesHandler у runserver
Command.get_handler = RunserverCommand.get_handler
