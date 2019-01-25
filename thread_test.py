# Use subprocess to wait for user input while playing 
# audio in the background

import subprocess
import os
import signal

COMMAND = "mplayer http://radio.tehiku.live:8030/stream"

class Player:
    def __init__(self):
        print('initialise')
        self.process = None

    def is_playing(self):
        return self.process is not None

    def play(self):
        if not self.is_playing():
            self.process = subprocess.Popen(COMMAND, 
                shell=True, # Run in a subshell so that the command doesn't mess with your shell
                stderr=subprocess.DEVNULL,  # You could send this to a pipe instead if you wanted to see what was going on 
                stdout=subprocess.DEVNULL, # You could send this to a pipe if you wanted to catch errors
                start_new_session=True) # This argument means that we can kill mplayer and all the child processes at once
            print('playing')
        else:
            print('already playing')

    def stop(self):
        if self.is_playing():
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM) # Kill all processes in the same process group
            self.process = None
            print('pause')
        else:
            print('already paused')

if __name__ == '__main__':
    player = Player()
    while True:
        choice = input("what do you want to do (1 = play; 2 = pause; else exit)?\n")
        if choice == '1':
            player.play()
        elif choice == '2':
            player.stop()
        else:
            break
    if player.is_playing():
        player.stop()
    print('Good-bye!')

