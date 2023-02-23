import json
import time
from urllib import request, error
import psycopg2
from dotenv import load_dotenv
import os
import random

load_dotenv()

postList = []
parentReply = []


def gather():
    url = 'https://www.reddit.com/.json?limit=1000'
    while True:
        try:
            response = request.urlopen(url)
            break
        except error.HTTPError as e:
            if e.code == 503 or e.code == 429:
                print("Reddit api is temporarily down. Retrying after 1 minute")
                time.sleep(60)
            else:
                raise e
    json_data = json.loads(response.read().decode())
    get_posts = json_data['data']['children']

    for post in get_posts:
        permalink = post['data'].get('permalink', None)
        if permalink:
            postList.append({'permalink': permalink})
    print(len(postList))
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
                if isinstance(e, error.HTTPError) and e.code == 429:
                    print("Reached maximum requests, waiting and retrying...")
                    time.sleep(random.randint(10, 20))
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
    conn = psycopg2.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('USER')} "
                            f"password={os.environ.get('PASSWORD')} port={os.environ.get('PORT')} host={os.environ.get('HOST')}")
    cur = conn.cursor()

    for message in parentReply:
        cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s', (message,))
        rows = cur.fetchall()
        if not rows:
            cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)', (message, "Reddit"))

    conn.commit()
    parentReply.clear()


while True:
    gather()
    time.sleep(random.randint(30, 60))
