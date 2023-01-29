from blockchain import * #blockchain.py
import time
from client import client
import sys
import json

length = 10

ts = [] # times taken to mine each block
nonces = [] # nonce of each block

c = client()
b = blockchain(c)
# c.reference(b)

for i in range(length):
    for x in range(20):
        # filling up each block with 20 bullshit transactions
        b.add_transaction(transaction("sender_sig", "spk", "rpk", 300, x, str(time.time())))
        
    #timing how long mining takes
    start = time.time()

    #mining 
    b.mine()
    
    end = time.time()
    ts.append(end-start)
    
    nonces.append(b.last_block().nonce)

print(b.get_block(100))
print("Average time/block:",sum(ts)/len(ts))
print("Nonces:",nonces)

# sys.exit()
c.send_money("skoobabadadada", 200)
