import os
import time


def au_sep(delay=0.3):
    print('---' * 40)
    time.sleep(delay)
    os.system("afplay /System/Library/Sounds/Ping.aiff")
    time.sleep(delay)
