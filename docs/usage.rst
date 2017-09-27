=====
Usage
=====

To use BlockRecord in a project::

    from blockrecord import BlockRecordRedis
    from my_redis_config import redis_instance
    # Start a new instance of the BlockRecord
    record = BlockRecordRedis(persistence=redis_instance)
    # Get a new block
    data = {'some': 'changes', 'to': 'data'}
    new_block = record.new_block(data=data)
    # Mine it to compute the hash
    new_block.mine()
    # Store it
    record.save_block_to_db(block=new_block)
    # Verify the chain of blocks you've mined haven't been tampered with
    assert record.verify_chain()
