import hashlib
import json
from datetime import datetime

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = {
            'index': 0,
            'timestamp': str(datetime.utcnow()),
            'data': 'Genesis Block',
            'previous_hash': '0',
            'hash': ''
        }
        genesis_block['hash'] = self.hash_block(genesis_block)
        self.chain.append(genesis_block)

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = {
            'index': len(self.chain),
            'timestamp': str(datetime.utcnow()),
            'data': data,
            'previous_hash': previous_block['hash'],
            'hash': ''
        }
        new_block['hash'] = self.hash_block(new_block)
        self.chain.append(new_block)

    def hash_block(self, block):
        # Exclude the hash itself when computing the hash
        block_string = json.dumps({
            'index': block['index'],
            'timestamp': block['timestamp'],
            'data': block['data'],
            'previous_hash': block['previous_hash']
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def get_chain(self):
        return self.chain

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current['previous_hash'] != previous['hash']:
                return False

            if current['hash'] != self.hash_block(current):
                return False

        return True

# ✅ Global blockchain instance to import anywhere
blockchain = Blockchain()
