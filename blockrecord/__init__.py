# -*- coding: utf-8 -*-

"""Top-level package for BlockRecord."""

__author__ = """Paul Hallett"""
__email__ = 'paulandrewhallett@gmail.com'
__version__ = '0.1.0'

from .block import Block  # noqa
from .record import AbstractBlockRecord, BlockRecordRedis  # noqa
