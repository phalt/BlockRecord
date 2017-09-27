#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `blockrecord` package."""
import pytest

from blockrecord import Block


@pytest.fixture
def genesis_block():
    data = [{'genesis': 'block'}]
    genesis = Block(data=data)
    genesis.mine()
    return genesis


def test_basic_block():
    # Data can be abritarily big and formatted how you like.
    data = [{'updates': [{'some': 'updates'}]}]
    # the genesis block has no previous_hash
    genesis = Block(data=data)
    # genesis block should have no nonce or previous_hash
    assert not genesis.nonce
    assert not genesis.previous_hash
    assert genesis.data == data
    # Lets mine it.
    resulting_hash = genesis.mine()
    assert resulting_hash.startswith('0000')
    assert genesis.nonce > 0
    # Make sure we can always reproduce the hash
    assert resulting_hash == genesis.hash(genesis.nonce)


def test_block_to_context(genesis_block):
    assert genesis_block.to_context() == {
        'uuid': str(genesis_block.uuid),
        'data': genesis_block.data,
        'previous_hash': genesis_block.previous_hash,
        'nonce': genesis_block.nonce,
        'hsh': genesis_block.hash(genesis_block.nonce)
    }


def test_block_with_parent(genesis_block):
    # Any data
    data = ['foo', 'bar']
    previous_hash = genesis_block.hash(genesis_block.nonce)
    second_block = Block(data=data, previous_hash=previous_hash)
    # Assert things
    assert not second_block.nonce
    assert second_block.previous_hash == previous_hash
    assert second_block.data == data
    resulting_hash = second_block.mine()
    assert resulting_hash.startswith('0000')
    assert second_block.nonce > 0
    # Make sure we can always preproduce the hash
    assert resulting_hash == second_block.hash(second_block.nonce)


def test_block_with_broken_parent_breaks_chain(genesis_block):
    # Any data
    data = ['foo', 'bar']
    previous_hash = genesis_block.hash(genesis_block.nonce)
    second_block = Block(data=data, previous_hash=previous_hash)
    # Assert things
    assert not second_block.nonce
    assert second_block.previous_hash == previous_hash
    assert second_block.data == data
    resulting_hash = second_block.mine()
    # Make sure we can always preproduce the hash
    assert resulting_hash == second_block.hash(second_block.nonce)
    # Change the original block
    genesis_block.data = ['omg wat']
    second_block.previous_hash = genesis_block.hash(genesis_block.nonce)
    second_result = second_block.hash(second_block.nonce)
    # The block chain should be broken as the previous hash has changed
    assert not resulting_hash == second_result
