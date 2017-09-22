# -*- coding: utf-8 -*-
from datetime import datetime
import hashlib
import os
import uuid

"""Main module."""

# Change the number of 0's to increase or decrease difficulty
MINED_VALID_VALUE = os.environ.get('MINED_VALID_VALUE', '0000')


class BlockRecord:
    """
    BlockRecord manages the creation of new Blocks and stores Blocks
    in the data store.
    """

    def __init__(self, *, redis):
        self.redis = redis


class Block:
    """
    A Block contains a single change of data.
    """

    def __repr__(self):
        return '<Block {}>'.format(self.uuid)

    def __init__(self, *, data=None, previous_hash=None):
        self.uuid = uuid.uuid4()
        self.nonce = None
        self.data = data
        self.previous_hash = previous_hash

    def hash(self, nonce=None):
        """
        Blocks are hashed in this format:

        =================================
        ||UUID|nonce|data|previous_hash||
        =================================
        """
        nonce = nonce or self.nonce

        message = hashlib.sha256()
        message.update(self.uuid.hex.encode('utf-8'))
        message.update(str(nonce).encode('utf-8'))
        message.update(str(self.data).encode('utf-8'))
        message.update(str(self.previous_hash).encode('utf-8'))

        return message.hexdigest()

    def _hash_is_valid(self, *, hsh):
        return hsh.startswith(MINED_VALID_VALUE)

    def mine(self):
        nonce = self.nonce or 0
        while True:
            hsh = self.hash(nonce=nonce)
            if self._hash_is_valid(hsh=hsh):
                self.nonce = nonce
                return hsh
            else:
                nonce += 1
