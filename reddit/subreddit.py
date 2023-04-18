import json
import time
from urllib import request, error
import psycopg2
import os
import random
import re
from sys import exit

subList = []
messages = []

os.system("")


class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'


def crawl():
    url3 = 'https://www.reddit.com/.json?limit=1000'
    while True:
        try:
            response = request.urlopen(url3)
            break
        except error.HTTPError as e:
            if e.code == 429 or e.code == 503:
                print(style.RED + 'Connection failed. Retrying...')
                time.sleep(random.randint(10, 20))
            else:
                raise e

    json_data = json.loads(response.read().decode())
    get_children = json_data['data']['children']

    for reply in get_children:
        scrap_messages = reply['data'].get('subreddit_name_prefixed', None)
        if scrap_messages:
            subList.append(scrap_messages)

    time.sleep(random.randint(10, 20))
    grab()


def grab():
    for sub in subList:
        url4 = f'https://www.reddit.com/{sub}/random.json?limit=1000'
        while True:
            try:
                response = request.urlopen(url4)
                break
            except error.HTTPError as e:
                if e.code == 429 or e.code == 503 or e.code == 500:
                    print(style.RED + 'Connection failed. Retrying...')
                    time.sleep(random.randint(10, 20))
                else:
                    raise e

        json_data = json.loads(response.read().decode())

        try:
            get_children = json_data[1]['data']['children'][1:]
        except KeyError as e:
            if e:
                print(style.YELLOW + "[Reddit]", end='')
                print(style.RED + "Encountered an error. Retrying...")
                time.sleep(random.randint(10, 20))
            else:
                raise e

        for reply in get_children:
            scrap_messages = reply['data'].get('body', None)
            if scrap_messages:
                messages.append(scrap_messages)

        time.sleep(random.randint(10, 20))
        logData()


def logData():
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASSWORD"],
            port=os.environ["PG_PORT"],
            host=os.environ["PG_HOST"]
        )

        cur = conn.cursor()

        for message in messages:
            message = re.sub(r"u/[^ ]+", "", message)
            if message:
                cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s', (message,))
                rows = cur.fetchall()
                if not rows:
                    print(style.YELLOW + "[Reddit]", end='')
                    print(style.GREEN + "Added", end=' ')
                    print(message)
                    cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)', (message, "Reddit"))

        conn.commit()
        messages.clear()
    except KeyError:
        print(style.YELLOW + "[Reddit]", end='')
        print(style.RED + "Missing or wrong DB credentials.")
        exit()


def call_subreddit():
    print("subreddit.py loaded successfully")
    while True:
        crawl()
        time.sleep(random.randint(30, 60))
