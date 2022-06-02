#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import logging
import logging.config
from paths import DUMP_HOME, WORK_NAME


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": "true",
    "formatters": {
        "short": {
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        },
        "default": {
            "class": "logging.Formatter",
            "format": "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)s - %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": os.path.join(DUMP_HOME, "%s.log" % WORK_NAME),
            "mode": "a+",
            "encoding": "utf-8"
        }
    },

    "loggers": {
        "console": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "file": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        }
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO"
    }
}


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("file")

