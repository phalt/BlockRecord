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

    def __init__(self, *, persistence, chain=None):
        """
        Args:
            persistence: The datastore you are persisting block records in.
            chain: A list of <Block> instances in the chain.
        """
        self.persistence = persistence
        self.chain = chain or []
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

    @abstractmethod
    def dump_blocks_to_db(self, *, uuid):
        """
        Dump all blocks in the current chain into the database.
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

    def verify_chain(self):
        """
        Verifies the entire chain of <Blocks> that we have, starting from the
        first one and moving forward.
        """
        for index, block in enumerate(self.chain):
            if index == 0:
                # It is the first block, so just calculate the hash
                prev_hash = block.hash(block.nonce)
            else:
                # It's along the chain, calculate the hash with the previous
                prev_block = self.chain[index - 1]
                if not prev_block.hash(prev_block.nonce) == prev_hash:
                    raise ValueError(
                        'Blockchain is broken at UUID %s', prev_block.uuid
                    )
                # Set previous hash as the current block
                prev_hash = block.hash(
                    nonce=block.nonce, previous_hash=prev_hash
                )
        return True


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

    def dump_blocks_to_db(self):
        """
        Stores all the blocks in self.chain in the database.
        """
        for block in self.chain:
            context = block.to_context()
            storage_key = '{}::{}'.format(STORAGE_KEY, str(block.uuid))
            self.persistence.set(storage_key, json.dumps(context))

    def save_block_to_db(self, *, block):
        """
        Stores a <Block> in Redis.
        """
        context = block.to_context()
        storage_key = '{}::{}'.format(STORAGE_KEY, str(block.uuid))
        self.persistence.set(storage_key, json.dumps(context))
        self.current_block_uuid = block.uuid
        self.current_block = block
        self.chain.append(block)

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
