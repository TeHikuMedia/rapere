## program in current state has the error that when run, it says it is 
#playing audio but nothing plays. Also keyboard interrupt does not stop 
#the program either: the only way to stop it is to exit the terminal

# Attempting to use multiprocessing to wait for user input while playing 
#audio in the background

import subprocess
from multiprocessing import Process, Queue
import time


def askInput(q):
    #uncommenting this line gives EOF errors as the program does not wait for the input to be received from user
    choice = input("listen? 0 = no change; 1 = start playing; 2 = stop") 
    #  i = 1
    print(choice)
    q.put(i)
    return True
    #print(q.get())


def listen(q):
    while askInput(q):
        pass 



def play_controls(q):
    global proc
    q = q.get()
    if q == 1:
        print('starting playing')
        proc = subprocess.Popen(["mplayer", "http://radio.tehiku.live:8030/stream < /dev/null > /dev/null 2>&1 &", ])
    elif q == 2:
        print('stop playing now')
        proc.kill()
        #code to stop playing
    elif q == 0:
        #keep things as they are, stopped or going
        pass


def main():
    q = Queue()
    q.put(1)
    p = Process(target=play_controls, args=(q,), daemon=True)
    #r = Process(target=listen, args=(q,))
    listen(q)
    p.start()
    #r.start()
    p.join()
    #r.join()
    
main()
