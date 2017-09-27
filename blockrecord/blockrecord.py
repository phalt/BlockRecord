# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import json
import os

from .block import Block

"""Main module."""

STORAGE_KEY = os.environ.get('BLOCK_RECORD_UUID', 'BLOCK_RECORD_UUID')
STORAGE_KEY_CURRENT_UUID = os.environ.get(
    'BLOCK_RECORD_CURRENT_BLOCK_UUID',
    'BLOCK_RECORD_CURRENT_BLOCK_UUID'
)


class AbstractBlockRecord(ABC):
    """
    AbstractBlockRecord is an AbstractBaseClass for rolling your
    own persistence layer beneath the BlockRecord.
    """

    def __init__(self, *, persistence):
        """
        Args:
            persistence: The datastore you are persisting block records in.
        """
        self.persistence = persistence
        self.current_block_uuid = self._get_current_block_uuid()
        if self.current_block_uuid:
            self.current_block = self._generate_current_block()
            self.verify_block(block=self.current_block)
        else:
            self.current_block = None

    @abstractmethod
    def _get_current_block_uuid(self):
        """
        Retrieves the most recent block UUID by looking for a key called
        BLOCK_RECORD_CURRENT_BLOCK_UUID.
        """

    @abstractmethod
    def _generate_current_block(self):
        """
        Generate a <Block> instance by looking in the persistence for the
        uuid that matches self.current_block_uuid.
        """

    @abstractmethod
    def save_block_to_db(self, *, block):
        """
        Save a <Block> in the persistence.
        """

    @abstractmethod
    def get_block(self, *, uuid):
        """
        Get a <Block> instance from its uuid.
        """

    def create_new_block(self, *, data):
        """
        Creates a brand new <Block> instance with the data and returns it.
        """
        if self.current_block:
            previous_hash = self.current_block.hash(self.current_block.nonce)
        else:
            previous_hash = None
        return Block(
            data=data, previous_hash=previous_hash
        )

    def verify_block(self, *, block):
        """
        Verifies a block by trying to compute Block's current hash
        against a new version of the hash with the nonce.

        If this returns False then it is likely that the Block's data
        has changed.
        """
        old_hash = block.hash
        if old_hash:
            assert old_hash == block.hash(block.nonce)
        else:
            raise ValueError('No previous hash on Block. Cannot verify')


class BlockRecordRedis(AbstractBlockRecord):
    """
    BlockRecordRedis stores Blocks in Redis.
    """

    def _get_current_block_uuid(self):
        """
        This BlockRecord uses Redis and we search for the
        STORAGE_KEY_CURRENT_UUID to retrive it.
        """
        if self.persistence.exists(STORAGE_KEY_CURRENT_UUID):
            return self.persistence.get(
                STORAGE_KEY_CURRENT_UUID
            ).decode('utf-8')
        else:
            return None

    def _generate_current_block(self):
        """
        Gets the Block data out of Redis.
        """
        result = self.persistence.get(
            '{}::{}'.format(STORAGE_KEY, self.current_block_uuid)
        )
        block_data = json.loads(result)
        return Block(
            uuid=block_data['uuid'],
            data=block_data['data'],
            previous_hash=block_data['previous_hash'],
            nonce=block_data['nonce'],
            hsh=block_data['hsh']
        )

    def save_block_to_db(self, *, block):
        """
        Stores a <Block> in Redis.
        """
        context = {
            'uuid': str(block.uuid),
            'data': block.data,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'hsh': block.hash(block.nonce)
        }
        storage_key = '{}::{}'.format(STORAGE_KEY, str(block.uuid))
        self.persistence.set(storage_key, json.dumps(context))
        self.current_block_uuid = block.uuid
        self.current_block = block

    def get_block(self, *, uuid):
        """
        Get a <Block> instance from its uuid.
        """
        storage_key = '{}::{}'.format(STORAGE_KEY, str(uuid))
        result = self.persistence.get(
            storage_key
        )
        block_data = json.loads(result)
        return Block(
            uuid=block_data['uuid'],
            data=block_data['data'],
            previous_hash=block_data['previous_hash'],
            nonce=block_data['nonce'],
            hsh=block_data['hsh']
        )
