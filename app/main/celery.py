import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


count_in_three_actions_schedule = {
    'count-links-3-task-binance': {
        'task': 'count.tasks.binance',
        'schedule': 20.0,
    },
    'count-links-3-task-bybit': {
        'task': 'count.tasks.bybit',
        'schedule': 20.0,
    },
    'count-links-3-task-kucoin': {
        'task': 'count.tasks.kucoin',
        'schedule': 20.0,
    },
    'count-links-3-task-huobi': {
        'task': 'count.tasks.huobi',
        'schedule': 20.0,
    },
    'count-links-3-task-okx': {
        'task': 'count.tasks.okx',
        'schedule': 20.0,
    },
}

count_in_two_actions_schedule = {
    'count-task-2': {
        'task': 'count.tasks.count_in_two',
        'schedule': 10.0,
    },
}

best_change_schedule = {
    'best-change-parsing-task': {
        'task': 'best_change_parsing.tasks.main',
        'schedule': 30.0,
    },
    'best-change-zip-task': {
        'task': 'best_change_zip.tasks.main',
        'schedule': 30.0,
    },
}

futures_schedule = {
    'okx-futures-task': {
        'task': 'futures.tasks.set_futures_okx',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 30.0,
    },
    'binance-futures-task': {
        'task': 'futures.tasks.set_futures_binance',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 30.0,
    },
    'bybit-futures-task': {
        'task': 'futures.tasks.set_futures_bybit',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 30.0,
    },
    'gateio-futures-task': {
        'task': 'futures.tasks.set_futures_gateio',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 30.0,
    },
    'bitget-futures-task': {
        'task': 'futures.tasks.set_futures_bitget',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 30.0,
    },
    'kucoin-futures-task': {
        'task': 'futures.tasks.set_futures_kucoin',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 30.0,
    },
    'huobi-futures-task': {
        'task': 'futures.tasks.set_futures_huobi',
        # 'schedule': crontab(hour=0, minute=0),
        'schedule': 30.0,
    },
}

parsing_spot_schedule = {
    'okx-parsing-spot-task': {
        'task': 'parsers.tasks.okx',
        'schedule': 10.0,
    },
    'binance-parsing-spot-task': {
        'task': 'parsers.tasks.binance',
        'schedule': 10.0,
    },
    'bybit-parsing-spot-task': {
        'task': 'parsers.tasks.bybit',
        'schedule': 10.0,
    },
    'gateio-parsing-spot-task': {
        'task': 'parsers.tasks.gateio',
        'schedule': 10.0,
    },
    'bitget-parsing-spot-task': {
        'task': 'parsers.tasks.bitget',
        'schedule': 10.0,
    },
    'kucoin-parsing-spot-task': {
        'task': 'parsers.tasks.kucoin',
        'schedule': 10.0,
    },
    'huobi-parsing-spot-task': {
        'task': 'parsers.tasks.huobi',
        'schedule': 10.0,
    },
}

app.conf.beat_schedule = {}
app.conf.beat_schedule.update(futures_schedule)
app.conf.beat_schedule.update(parsing_spot_schedule)
app.conf.beat_schedule.update(best_change_schedule)
app.conf.beat_schedule.update(count_in_two_actions_schedule)
app.conf.beat_schedule.update(count_in_three_actions_schedule)