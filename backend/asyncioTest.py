import threading
import time
import app
A = 0

def printA(i, e,f):
    global A
    time.sleep(i)
    A += 1
    threading.Thread(daemon=True, target=lambda: print(f'                F={f} E={e} I={i} A={A}')).start()


def printB(e,f):
    global A
    time.sleep(e)
    A += 1
    print(f'        F={f} e={e} A={A}')
    for i in range(10):
        threading.Thread(daemon=True, target=lambda: printA(i, e,f)).start()

def printD(e):
    time.sleep(e*10)
    print("             ",e)

def printC(f):
    A = 0
    while True:
        time.sleep(f)
        print(f'    F={f} A={A}')
            
