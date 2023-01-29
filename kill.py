import os
import shutil
di = os.getcwd()
import sys


# os.system('taskkill /F /IM "wt.exe"')
if len(sys.argv) <= 1:
    os.system('taskkill /F /IM "python.exe" && python kill.py 1')

os.system('taskkill /F /IM "cmd.exe"')

#clean
try:
    shutil.rmtree('./testenv/')
except:
    pass
