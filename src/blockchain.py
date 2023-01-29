from hashlib import sha256
import json
import time
from client import transaction

blocksize = 20 # total transactions per block


class block:
    def __init__(self, index, transactions, timestamp, previous_hash, miner="", nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = str(timestamp)
        self.previous_hash = previous_hash
        self.nonce = nonce  # bro got the nonce
        self.miner = miner
        self.gen_hash()
        
    def gen_hash(self):
        tr = []
        for x in self.transactions:
            tr.append(x.string())
        
        block_string = json.dumps([self.index, tr, self.timestamp, self.previous_hash, self.miner, self.nonce])
        
        self.hash = sha256(block_string.encode()).hexdigest()

    def insert_transaction(self, dat):
        self.transactions.append(transaction(
            dat[2],
            dat[0],
            dat[1],
            dat[3],
            dat[4],
            dat[5]
        ))

class blockchain:
    def __init__(self, client):
        self.client = client
        self.client.reference(self)
        print("Class reference created")
        self.unconfirmed_transactions = []
        self.create_genesis_block()
        
    def create_genesis_block(self):
        if self.get_block(0):
            return 
        genesis_block = block(0, [], str(time.time()), "0")
        self.addblock(genesis_block)

    def last_block(self):
        return self.get_block(-1)

    def get_block(self, block_index):
        try:
            if block_index <0:
                q = "SELECT DISTINCT * FROM blockchain ORDER BY block_id DESC LIMIT 1 OFFSET ?;"
                # r = "SELECT DISTINCT * FROM transactions ORDER BY block_id DESC LIMIT 1 OFFSET ?"
                block_index += 1
                block_index *= -1
            else:
                q = """
                    SELECT * FROM blockchain WHERE block_id=?;
                """
            
            r = """
                SELECT * FROM transactions WHERE block_id=? ORDER BY transaction_id;
            """
            
            self.client.c.execute(q, (str(block_index),))
            bc = self.client.c.fetchall()[0]
            
            block_index = int(bc[0])
            self.client.c.execute(r,( str(block_index),))
            
            tr = self.client.c.fetchall()
    
            b = block(block_index, [], bc[3], bc[2], bc[5], bc[4])
            for d in tr:
                b.insert_transaction(d)
            b.gen_hash()
            return b
        except:
            return None

    def proofofwork(self, b, difficulty):
        b.difficulty = difficulty
        # print("Mining Block #"+str(b.index))
        # print("Difficulty =",difficulty)
        b.gen_hash()

        
        while not int(b.hash, 16) <= 1 << (256 - difficulty):  # this is absolutely mad my dad showed me this
            b.nonce+=1
            b.gen_hash()
        # print("Nonce Found:",b.nonce)

    def reward(self, block_index):
        return 50/(2**(block_index * (1/210000)))
        
    def addblock(self, b):
        b.gen_hash()
        if b.index != 0 and self.last_block().hash != b.previous_hash:
            print("j")
            return False

        if b.index != 0 and not self.is_valid_proof(b):
            print("i")
            return False
        

        #add to database
        self.client.c.execute("""
            INSERT INTO blockchain(block_id, hash, previous_hash, timestamp, nonce, miner, reward) VALUES (?,?,?,?,?,?,?)
        """, (b.index, b.hash, b.previous_hash, b.timestamp, b.nonce, b.miner, self.reward(b.index)))

        for t in b.transactions:
            self.client.c.execute("""
                INSERT INTO transactions(sender_pk, recipient_pk, sender_sig, total, transaction_id, timestamp, block_id) VALUES (?,?,?,?,?,?,?)
            """, (t.sender_pk, t.recipient_pk, t.sender_sig, t.total, t.id, t.timestamp, b.index))
        self.client.connection.commit()
        return True
        
    def is_valid_proof(self, b):
        b.gen_hash()
        print((int(b.hash,16) <= 1 << (256 - b.difficulty)))
        return (int(b.hash,16) <= 1 << (256 - b.difficulty)) 
        

    def add_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def mine(self):
        if len(self.unconfirmed_transactions) < blocksize: # if there arent enough transactions, dont bother
            return False

        last_block = self.last_block()
        new_block = block(last_block.index+1, self.unconfirmed_transactions, str(time.time()), last_block.hash, miner=str(self.client.pk.export_key()))
        
        self.proofofwork(new_block, 10) # change difficulty in the ui (it doesnt matter what it is, but the block which has proof of work with the highest difficulty will be selected by other peers)
        print(new_block.nonce)  
        self.addblock(new_block)
        self.unconfirmed_transactions = []
        return new_block.index

