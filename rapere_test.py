## Run this file to test all the required packages are installed

import led_listen

if led_listen.BREADBOARD:
    led_listen.setup_pins()
filename = "rapere_test_audio.wav"
player = led_listen.Player()
led_listen.do_something(filename, player)

