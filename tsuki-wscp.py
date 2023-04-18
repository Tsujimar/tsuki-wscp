from sys import platform, argv, exit
import subprocess
import sys
import threading

sys.path.append("/4Chan")
sys.path.append("/reddit")

from fourchan.board import call_crawler
from reddit.heart import call_gather
from reddit.randomized import call_randomizer
from reddit.subreddit import call_subreddit


def launch_threads(delay, optional_nsfw):
    t1 = threading.Thread(target=call_crawler, args=(delay, optional_nsfw))
    t2 = threading.Thread(target=call_gather)
    t3 = threading.Thread(target=call_randomizer)
    t4 = threading.Thread(target=call_subreddit)

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()


def init_harvester():
    optional_nsfw = False
    if len(argv) < 3 or argv[1] != "-s":
        print("Usage: python3 tsuki-wscp [-s {1-5}] [--nsfw-toggle]")
        exit()
    if int(argv[2]) < 1 or int(argv[2]) > 5:
        print("Enter a value between 1-5")
        exit()
    if len(argv) == 4:
        if argv[3] == "--nsfw-toggle":
            delay = int(argv[2])
            optional_nsfw = True
            launch_threads(delay, optional_nsfw)
        else:
            print(f"Optional parameter is [--nsfw-toggle] not [{argv[3]}]")
            exit()
    elif len(argv) > 4:
        print("Too many arguments")
        exit()

    elif len(argv) == 3:
        delay = int(argv[2])
        launch_threads(delay, optional_nsfw)


if platform == "linux":
    bashrc_path = '.bashrc'
    subprocess.call(["/usr/bin/bash", "-i", "-c", "source " + bashrc_path])
    init_harvester()
else:
    init_harvester()
