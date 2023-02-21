import json
import time
from urllib import request
import psycopg2
from dotenv import load_dotenv
import os
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
        title = post['data'].get('title', None)
        if permalink and title:
            postList.append({'permalink': permalink, 'title': title})
    crawl()


def crawl():
    max_count = 100
    current_count = 0
    for link in postList:
        target = link['permalink']
        url2 = f'https://www.reddit.com{target}.json'
        response = request.urlopen(url2)
        json_data = json.loads(response.read().decode())
        get_children = json_data[1]['data']['children'][1:]

        for reply in get_children:
            scrap_messages = reply['data'].get('body', None)
            parentReply.append(scrap_messages)
            current_count += 1
            if current_count == max_count:
                break
        if current_count == max_count:
            break
        time.sleep(1)
        print(parentReply)
        logData()
        current_count = 0
        time.sleep(60)


def logData():
    conn = psycopg2.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('USER')} "
                            f"password={os.environ.get('PASSWORD')} port={os.environ.get('PORT')} host={os.environ.get('HOST')}")
    cur = conn.cursor()

    for message in parentReply:
        cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)', (message, "Reddit"))
    conn.commit()
    parentReply.clear()


gather()
