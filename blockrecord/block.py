import hashlib
import os
import uuid as uuid_lib


MINED_VALID_VALUE = os.environ.get('MINED_VALID_VALUE', '0000')


class Block:
    """
    A Block contains a single change of data.
    """

    def __repr__(self):
        return '<Block {}>'.format(self.uuid)

    def __init__(
        self, *,
        uuid=None,
        data=None,
        previous_hash=None,
        nonce=None,
        hsh=None
    ):
        if isinstance(uuid, str):
            uuid = uuid_lib.UUID(uuid)
        self.uuid = uuid or uuid_lib.uuid4()
        self.nonce = nonce
        self.data = data
        self.previous_hash = previous_hash
        self.hsh = hsh

    def hash(self, nonce=None, previous_hash=None):
        """
        Blocks are hashed in this format:

        =================================
        ||UUID|nonce|data|previous_hash||
        =================================
        """
        nonce = nonce or self.nonce
        previous_hash = previous_hash or self.previous_hash
        message = hashlib.sha256()
        message.update(self.uuid.hex.encode('utf-8'))
        message.update(str(nonce).encode('utf-8'))
        message.update(str(self.data).encode('utf-8'))
        message.update(str(previous_hash).encode('utf-8'))

        return message.hexdigest()

    def _hash_is_valid(self, *, hsh):
        return hsh.startswith(MINED_VALID_VALUE)

    def mine(self):
        nonce = self.nonce or 0
        while True:
            hsh = self.hash(nonce=nonce)
            if self._hash_is_valid(hsh=hsh):
                self.nonce = nonce
                self.hsh = hsh
                return hsh
            else:
                nonce += 1


    def to_context(self):
        return {
            'uuid': str(self.uuid),
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hsh': self.hash(self.nonce)
        }
