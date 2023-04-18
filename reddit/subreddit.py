import json
import time
from urllib import request, error
import psycopg2
import os
import random
import re

subList = []
messages = []


def crawl():
    url3 = 'https://www.reddit.com/.json?limit=1000'
    while True:
        try:
            response = request.urlopen(url3)
            break
        except error.HTTPError as e:
            if e.code == 429 or e.code == 503:
                print('Connection failed. Retrying...')
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
                    print('Connection failed. Retrying...')
                    time.sleep(random.randint(10, 20))
                else:
                    raise e

        json_data = json.loads(response.read().decode())

        try:
            get_children = json_data[1]['data']['children'][1:]
        except KeyError as e:
            if e:
                print("Encountered an error. Retrying...")
                time.sleep(random.randint(10, 20))
            else:
                raise e

        for reply in get_children:
            scrap_messages = reply['data'].get('body', None)
            if scrap_messages:
                messages.append(scrap_messages)

        time.sleep(random.randint(10, 20))
        print(f"Iterating through {len(messages)}...")
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
                    print(f"Added {message}")
                    cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)', (message, "Reddit"))

        conn.commit()
        print("Added messages successfully to DB, returning")
        messages.clear()
    except KeyError:
        print("Missing or wrong DB credentials.")


def call_subreddit():
    print("subreddit.py loaded successfully")
    while True:
        crawl()
        time.sleep(random.randint(30, 60))
