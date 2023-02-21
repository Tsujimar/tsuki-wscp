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
    url = 'https://www.reddit.com/.json'
    response = request.urlopen(url)
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
            except error.HTTPError as e:
                if e.code == 429:
                    print("Reached maximum requests, waiting and retrying...")
                    time.sleep(random.randint(10, 20))
                else:
                    raise e

        json_data = json.loads(response.read().decode())
        get_children = json_data[1]['data']['children'][1:]

        for reply in get_children:
            scrap_messages = reply['data'].get('body', None)
            parentReply.append(scrap_messages)

        time.sleep(random.randint(10, 20))
        print(parentReply)
        logData()


def logData():
    conn = psycopg2.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('USER')} "
                            f"password={os.environ.get('PASSWORD')} port={os.environ.get('PORT')} host={os.environ.get('HOST')}")
    cur = conn.cursor()

    for message in parentReply:
        cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)', (message, "Reddit"))
    conn.commit()
    parentReply.clear()


gather()