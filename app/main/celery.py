import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # 'count-links-3-task-binance': {
    #     'task': 'count_links_3.tasks.binance',
    #     'schedule': 20.0,
    # },
    # 'count-links-3-task-bybit': {
        # 'task': 'count_links_3.tasks.bybit',
        # 'schedule': 20.0,
    # },
    # 'count-links-3-task-kucoin': {
    #     'task': 'count_links_3.tasks.kucoin',
    #     'schedule': 20.0,
    # },
    # 'count-links-3-task-huobi': {
    #     'task': 'count_links_3.tasks.huobi',
    #     'schedule': 20.0,
    # },
    # 'count-links-3-task-okx': {
    #     'task': 'count_links_3.tasks.okx',
    #     'schedule': 20.0,
    # },

    # 'best-change-parsing-task': {
    #     'task': 'best_change_parsing.tasks.main',
    #     'schedule': 30.0,
    # },
    # 'best-change-zip-task': {
    #     'task': 'best_change_zip.tasks.main',
    #     'schedule': 30.0,
    # },

    'count-task': {
        'task': 'count.tasks.main',
        'schedule': 10.0,
    },

    'okx-task': {
        'task': 'parsers.tasks.okx',
        'schedule': 10.0,
    },
    # 'binance-task': {
    #     'task': 'parsers.tasks.binance',
    #     'schedule': 10.0,
    # },
    # 'bybit-task': {
    #     'task': 'parsers.tasks.bybit',
    #     'schedule': 10.0,
    # },
    'okx-task': {
        'task': 'parsers.tasks.okx',
        'schedule': 10.0,
    },
    'gateio-task': {
        'task': 'parsers.tasks.gateio',
        'schedule': 10.0,
    },
    'bitget-task': {
        'task': 'parsers.tasks.bitget',
        'schedule': 10.0,
    },
    'kucoin-task': {
        'task': 'parsers.tasks.kucoin',
        'schedule': 10.0,
    },
    'huobi-task': {
        'task': 'parsers.tasks.huobi',
        'schedule': 10.0,
    },
}
