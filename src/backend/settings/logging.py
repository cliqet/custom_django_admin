import logging
from typing import Literal


class DjangoRQFilter(logging.Filter):
    def filter(self, record):
        if record.name == 'rq.worker':
            return record.levelno >= logging.WARNING
        return True

    
def get_logging_config(ENV: dict) -> dict:
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': ENV.logging_config.file_handler.log_level, 
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': f'{ENV.logging_config.file_handler.log_path}/app.log',
                'formatter': 'verbose',
                'maxBytes': ENV.logging_config.file_handler.max_bytes,  
                'backupCount': ENV.logging_config.file_handler.backup_count,
                'filters': ['django_rq_filter']
            },
            'console': {
                'level': ENV.logging_config.console_handler.log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'formatters': {
            'verbose': {
                'format': '{asctime} {levelname} [{name}:{lineno}] {message}',
                'style': '{',
                'datefmt': '%Y-%m-%dT%H:%M:%S%z'
            },
        },
        'filters': {
            'django_rq_filter': {
                '()': DjangoRQFilter,
            },
        },
        'root': {
            'handlers': ENV.logging_config.handlers,
            'level': 'DEBUG',
        },
    }


LOG_CONTEXT_TYPE = Literal[
    'LOGIN_SUCCESS', 'CHANGE_PASSWORD_SUCCESS', 'GENERAL_ERROR',
    'EMAIL_SUCCESS', 'EMAIL_ERROR', 'GENERAL_DEBUG', 'GENERAL_INFO', 
]

class LoggerContext:
    """
        Object to hold the context of a log.
        NOTE: Do not put a non-serializable value!!!
    """
    def __init__(self, type: LOG_CONTEXT_TYPE, context: dict = {}):
        self.type = type
        self.context = context