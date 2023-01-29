import os
import shutil
di = os.getcwd()
import sys
from distutils.dir_util import copy_tree


# os.system('taskkill /F /IM "wt.exe"')
if len(sys.argv) <= 1:
    os.system('taskkill /F /IM "python.exe" && python init.py 1')

os.system('taskkill /F /IM "cmd.exe"')

#clean
try:
    shutil.rmtree('./testenv/')
except:
    pass

#make

try:
    os.mkdir("./testenv")
except:
    pass

os.mkdir("./testenv/1")
os.mkdir("./testenv/2")

files = [
    "src/blockchain.py",
    "src/client.py",
    # "blockchain.db"
]
offset = 0
for x in ["testenv/1", "testenv/2"]:
    os.mkdir(x+"/keyfiles")
    for f in files:
        shutil.copy(f, x)

    copy_tree("src/p2p", x)
    if "2" in x:
        shutil.copy("blockchain.db", x)
    f = open(x+"/.env", "w")
    f.write("""PORT="""+str(44444+offset))

    offset += 5
    print(di + x)
    os.system('start /D "' + di + "\\" + x + '" python client.py')
    os.system('start /D "' + di + "\\" + x + '" node index')
    print(x)



