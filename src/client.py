from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import sqlite3
import psutil
from pythonp2p import Node
import time
import sys
import json
import ast
# addrs = psutil.net_if_addrs()

class transaction:
    def __init__(self, sender_sig, sender_pk, recipient_pk, total, id, timestamp):
        self.sender_sig = sender_sig
        self.sender_pk = sender_pk
        self.recipient_pk = recipient_pk
        self.total = total
        self.id = id
        self.timestamp = timestamp
        
    def string(self):
        return str([self.sender_pk ,self.recipient_pk, self.total, self.id])

class client(Node):
    def __init__(self):
        f = open("env.json", "r")
        self.port = int(json.loads(f.read())["port"])
        f.close()
        super(client, self).__init__("0.0.0.0", self.port, self.port+1)


        self.start()

        self.addfile("blockchain.db")


        print("RUNNING ON PORT: ", self.port)
        try: # load client's key files (if they exist)
            #load public key
            f = open("keyfiles/pk.pem", "r") 
            self.pk = RSA.import_key(f.read())

            # load secret/private key
            f = open("keyfiles/sk.pem", "r")
            self.sk = RSA.import_key(f.read())
        
        except:
            self.sk = None
            self.pk = None
            print("DEBUG> No keyfiles found, generating new keypair...") # this is shit because if a client loses their keyfiles they lose all of their money

            # Generate public & private keypair

            # Secret key (SK)
            
            self.sk = RSA.generate(2048)
            file_out = open("keyfiles/sk.pem", "wb")
            file_out.write(self.sk.export_key())
            file_out.close()

            # Public Key (PK)
            self.pk = self.sk.publickey()
            file_out = open("keyfiles/pk.pem", "wb")
            file_out.write(self.pk.export_key())
            file_out.close()

        
        self.signer = PKCS1_v1_5.new(self.sk)
        # self.verifier = PKCS1_v1_5.new(self.pk)

        self.connection = sqlite3.connect("blockchain.db")
        self.c = self.connection.cursor()
        
        self.c.execute("""
        CREATE TABLE if not exists blockchain (
            block_id integer,
            hash text,
            previous_hash text,
            timestamp text,
            nonce integer,
            miner text,
            reward real,
            PRIMARY KEY (block_id)
        )
        """)
        
        self.c.execute("""
        CREATE TABLE if not exists transactions (
            sender_pk text,
            recipient_pk text,
            sender_sig text,
            total real,
            transaction_id integer,
            timestamp text,
            block_id integer,
            FOREIGN KEY (block_id) REFERENCES blockchain (block_id) 
            ON DELETE CASCADE ON UPDATE NO ACTION,
            PRIMARY KEY (block_id, transaction_id)
        )
        """)
        self.connection.commit()

        self.initiate_p2p()

    def initiate_p2p(self, p_offset=0):
        self.connect_to("127.0.0.1", self.port+5)

        self.send_money("spk", 400)
        # self.net.addfile()
    
    def reference(self, b):
        self.blockchain = b

    def get_balance(self, pk):
        #get outgoing transactions
        self.c.execute("""
        select (ifnull(total_in,0) + ifnull(total_reward,0) - ifnull(total_out, 0)) as total from (select sum(total) as total_in from transactions where recipient_pk=?), 
(select sum(reward) as total_reward from blockchain where miner=?),
(select sum(total) as total_out from transactions where sender_pk=?) 
        """, (pk, pk, pk))
        print(self.c.fetchall())
    def on_message(self, m, r, p):
        # try:
        data = json.loads(m)

        if not data['header']:
            return
        
        if data['header'] == 'transaction':
            t = transaction(
                data['data']['sender_sig'],
                data['data']['sender_pk'],
                data['data']['recipient_pk'],
                float(data['data']['total']),
                int(data['data']['id']),
                data['data']['timestamp']
            )


            self.get_balance(data['data']['sender_pk'])
            if self.verify_transaction(t):
                self.blockchain.add_transaction(t)

        # except:
        #     return
    def request_blockchain_updates(self):
        #ask the network for the current block height and a hash of the current blockchain database
        self.c.execute("SELECT MAX(block_id) FROM blockchain")
        f = self.c.fetchall()
        print(f)
        self.send_message(
            json.dump({
                "header":"blockchain_updates",
                "data": {
                    "block_height":int(f[0][0])
                }
            })
        )

    def gen_block_updates(self, height):
        self.c.execute("SELECT * FROM blockchain WHERE block_id > ?;", height)
        b = self.c.fetchall()
        self.c.execute("SELECT * FROM transactions WHERE block_id > ?;", height)
        t = self.c.fetchall()
        print(b)
        print(t)

        # arrange these updates into json file

        #compress json file
        #gen file hash
        #respond with data containing new block height'


    def send_money(self, recipient_pk, total):
        t = transaction(
            None,
            self.pk.export_key().decode(),
            recipient_pk, 
            total,
            self.calculate_transaction_number(recipient_pk),
            str(time.time())
        )

        t = self.sign_transaction(t)
        self.t_test = t
        data = json.dumps({
            "header": "transaction",
            "data": {
            "sender_sig": t.sender_sig,
            "sender_pk": t.sender_pk,
            "recipient_pk": t.recipient_pk,
            "total": t.total,
            "id": t.id,
            "timestamp": t.timestamp
        }})

        self.send_message(data)

    def calculate_transaction_number(self, recipient_pk):
        s = self.pk.export_key().decode()

        self.c.execute("""
            SELECT COUNT(*) FROM TRANSACTIONS WHERE sender_pk=(?) AND recipient_pk=(?)
        """, (s, recipient_pk))
        plus = 0
        for x in self.blockchain.unconfirmed_transactions:
            if x.recipient_pk == recipient_pk and x.sender_pk == s:
                plus += 1

        return self.c.fetchall()[0][0] + plus
        
    def sign_transaction(self, t):
        # Before the client actually signs and approves the transaction, the user should be prompted wether they want to make this transaction

        # only the sender needs to sign the transaction
        if t.sender_pk != self.pk.export_key().decode():
            return False
        
        data = str([
            t.sender_pk ,
            t.recipient_pk,
            float(t.total),
            int(t.id),
            str(t.timestamp)
        ])
        
        hashed_data = SHA256.new(data.encode())
        
        t.sender_sig = self.signer.sign(hashed_data).hex() # encrypt the data with client's secret key

        return t

    def verify_transaction(self, t):
        data = str([
            t.sender_pk,
            t.recipient_pk,
            float(t.total),
            int(t.id),
            str(t.timestamp)
        ])
        
        hashed_data = SHA256.new(data.encode())
        verifier = PKCS1_v1_5.new(RSA.import_key(t.sender_pk))
        
        res = verifier.verify(hashed_data, bytes.fromhex(t.sender_sig))
        return res

    

