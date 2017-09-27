#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `blockrecord` using redis as a datastore."""
import pytest
from redis import StrictRedis

from blockrecord import Block, BlockRecordRedis


@pytest.fixture
def redis_instance():
    return StrictRedis(
        host='localhost',
        port='6379',
    )


def test_init_block_record_redis(redis_instance):
    record = BlockRecordRedis(persistence=redis_instance)
    assert record.current_block_uuid is None


def test_generate_genesis_block_and_save_it_return_it(redis_instance):
    record = BlockRecordRedis(persistence=redis_instance)
    genesis = record.create_new_block(data={'genesis': 'block'})
    assert isinstance(genesis, Block)
    genesis.mine()
    assert genesis.hsh.startswith('0000')
    record.save_block_to_db(block=genesis)
    assert record.current_block_uuid == genesis.uuid
    new_genesis = record.get_block(uuid=genesis.uuid)
    # They should result in identical hashes
    assert new_genesis.hash(new_genesis.nonce) == genesis.hash(genesis.nonce)


def test_verify_chain_works_with_big_list_of_blocks(redis_instance):
    genesis_block = Block(data={'value': 123})
    genesis_block.mine()
    chain = [genesis_block]
    previous_hash = genesis_block.hsh
    for x in range(3):
        block = Block(data={'value': x}, previous_hash=previous_hash)
        previous_hash = block.mine()
        chain.append(block)

    record = BlockRecordRedis(persistence=redis_instance, chain=chain)
    assert record.verify_chain()
