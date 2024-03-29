import json
import time
from urllib import request, error
import psycopg2
from psycopg2 import OperationalError
import os
import random
import re
from sys import exit

postList = []
parentReply = []

os.system("")


class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'


def gather():
    url = 'https://www.reddit.com/.json?limit=1000'
    while True:
        try:
            response = request.urlopen(url)
            break
        except error.HTTPError as e:
            if e.code == 503 or e.code == 429:
                print(style.YELLOW + "[Reddit]", end='')
                print(style.RED + "Api is temporarily down. Retrying after 1 minute")
                time.sleep(60)
            else:
                raise e
    json_data = json.loads(response.read().decode())
    get_posts = json_data['data']['children']

    for post in get_posts:
        permalink = post['data'].get('permalink', None)
        if permalink:
            postList.append({'permalink': permalink})
    crawl()


def crawl():
    for link in postList:
        target = link['permalink']
        url2 = f'https://www.reddit.com{target}.json'

        while True:
            try:
                response = request.urlopen(url2)
                break
            except (error.HTTPError, UnicodeEncodeError) as e:
                if isinstance(e, error.HTTPError):
                    if e.code == 429:
                        print(style.YELLOW + "[Reddit]", end='')
                        print(style.RED + "Reached maximum requests, waiting and retrying...")
                        time.sleep(random.randint(10, 20))
                    else:
                        raise e
                elif isinstance(e, UnicodeEncodeError):
                    print(style.YELLOW + "[Reddit]", end='')
                    print(style.RED + "Encountered a UnicodeEncodeError: " + str(e) + ". Retrying...")
                    crawl()
                else:
                    raise e

        json_data = json.loads(response.read().decode())
        get_children = json_data[1]['data']['children'][1:]

        for reply in get_children:
            scrap_messages = reply['data'].get('body', None)
            if scrap_messages:
                parentReply.append(scrap_messages)

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

        for message in parentReply:
            message = re.sub(r"u/[^ ]+", "", message)
            cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s', (message,))
            rows = cur.fetchall()
            if not rows:
                print(style.YELLOW + "[Reddit]", end='')
                print(style.GREEN + "Added", end=' ')
                print(style.RESET + message)
                cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)', (message, "Reddit"))

        conn.commit()
        parentReply.clear()
    except Exception as e:
        if type(e) == KeyError:
            print(style.YELLOW + "[Reddit]", end='')
            print(style.RED + "DB service inactive")
            exit()
        elif type(e) == OperationalError:
            print(style.YELLOW + "[Reddit]", end='')
            print(style.RED + "Missing or wrong DB credentials.")
            exit()


def call_gather():
    print(style.RESET + "heart.py loaded successfully")
    while True:
        gather()
        time.sleep(random.randint(30, 60))
