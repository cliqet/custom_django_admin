# ruff: noqa: F403, F405
import logging

from backend.settings.base import *

log = logging.getLogger(__name__)

# Your staging settings

log.info(f'Staging settings loaded')