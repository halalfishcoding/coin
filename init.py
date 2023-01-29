import os
import shutil
di = os.getcwd()
import sys


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
    "src/main.py"
]
offset = 0
for x in ["testenv/1", "testenv/2"]:
    os.mkdir(x+"/keyfiles")
    for f in files:
        shutil.copy(f, x)
    
    f = open(x+"/env.json", "w")
    f.write("""{
    "port": """+str(44444+offset)+"""
}""")
    offset += 5
    print(di + x)
    os.system('start /D "' + di + "\\" + x + '" python main.py')
    print(x)



