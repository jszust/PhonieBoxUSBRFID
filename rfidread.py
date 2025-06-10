#!/usr/bin/env python
import evdev
import subprocess
import re
import tempfile
from evdev import categorize, ecodes
from collections import deque
global tag
tmp = tempfile.NamedTemporaryFile()
prevtrack = '0011127231'
shutdown = '0011135575'
reboot = '0011167491'

class Device():

    @classmethod
    def connect(cls):
        # connect to device if available
        try:
            device = evdev.InputDevice('/dev/input/event0')
            return device
        except IndexError:
            exit()

    @classmethod
    def run(cls):
        device = cls.connect()
        container = []
        try:
            device.grab()
            # bind the device to the script
            for event in device.read_loop():
                    # enter into an endeless read-loop
                    if event.type == ecodes.EV_KEY and event.value == 1:
                        digit = evdev.ecodes.KEY[event.code]
                        URI = ""
                        tag = ""
                        one_before_last = ""
                        if digit == 'KEY_ENTER':
                            # create and dump the tag
                            tag = "".join(i.strip('KEY_') for i in container)
                            container = []
                            # Write tag to temp file
                            if tag.strip() == prevtrack.strip():
                                command = 'mpc prev'
                            elif tag.strip() == reboot.strip():
                                command = 'sudo reboot'
                            elif tag.strip() == shutdown.strip():
                                command = 'sudo shutdown'
                            else:
                                #Write tag name to tempfile
                                with open(tmp.name,'a') as f:
                                    f.write('\r' + tag)
                                # Determine last card swiped
                                tmp.seek(0)
                                with open(tmp.name, 'r') as f:
                                    one_before_last = deque(f, 2)[0]
                                # Create a blank URI string
                                linenum = 0
                                s = ""
                                # Create a pattern regex string
                                pattern = re.compile(tag)
                                # Search for tag and return URI of associated ID
                                with open ('/home/{user}/cards.txt', 'rt') as myfile:
                                    for line in myfile:
                                        linenum += 1
                                        if pattern.search(line) != None:
                                            URI = re.search(r'"(.*?)"',line).group(1)
                                if tag.strip() == one_before_last.strip():
                                    command = 'mpc next'
                                elif URI == s:
                                    command = ''
                                else:
                                    command = 'mpc stop -q && mpc clear -q && mpc add "' + URI + '" && mpc play'
                            subprocess.run(command, capture_output=True, shell=True)
#                            print(command)
                        else:
                            container.append(digit)
            tmp.close()
        except:
            # catch all exceptions to be able release the device
            device.ungrab()

Device.run()
