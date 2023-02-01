import os
import shutil
import sys
from distutils.dir_util import copy_tree
import time

di = os.getcwd()
# os.system('taskkill /F /IM "wt.exe"')
if len(sys.argv) <= 1:
    try:
        os.system('taskkill /F /IM "node.exe"')
    except:
        pass
    os.system('taskkill /F /IM "python.exe" && python init.py 1')

os.system('taskkill /F /IM "cmd.exe"')

#clean
try:
    # shutil.rmtree('./testenv/')
    for x in ["testenv/1/", "testenv/2/"]:
        for y in ["blockchain.py", "client.py", "index.js", "seed.json", ".env"]:
            os.remove(x+y)
except:
    pass

#make

try:
    os.mkdir("./testenv")
except:
    pass

try:
    os.mkdir("./testenv/1")
    os.mkdir("./testenv/2")
except:
    pass

files = [
    "src/blockchain.py",
    "src/client.py",
    "src/index.js",
    # "src/"
    # "blockchain.db"
]
offset = 0
initoffset = 5

for x in ["testenv/2", "testenv/1"]:
    if "1" in x:
        time.sleep(2)
    try:
        os.mkdir(x+"/keyfiles")
    except:
        pass

    for f in files:
        shutil.copy(f, x)

    # if "2" in x:
    #     shutil.copy("blockchain.db", x)

    f = open(x+"/.env", "w")
    f.write("""
PORT="""+str(3999+offset)+"""
P2P_PORT="""+str(44445+offset)+"""
    """)
    
    f.close()

    f = open(x+'/seed.json', "w")
    if "1" in x:
        f.write ("""
    {"seed": [
        "ws://127.0.0.1:"""+str(44445+initoffset - offset)+""""
    ]}
    """)
    else:
        f.write("""{"seed":[]}""")
    f.close()

    f = open(x+"/env.json", "w")
    f.write("""{"port":"""+str(3999+offset)+"""}""")
    f.close()



    offset += 5
    # if ["2"] in x:

    os.system('start /D "' + di + "\\" + x + '" cmd /k python client.py')
    os.system('start /D "' + di + "\\" + x + '" cmd /k node index')





