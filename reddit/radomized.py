import json
import time
from urllib import request, error
import psycopg2
from dotenv import load_dotenv
import os
import random
import re

load_dotenv()

secondaryParent = []


def crawl():
    url3 = 'https://www.reddit.com/random.json?limit=1000'
    while True:
        try:
            response = request.urlopen(url3)
            break
        except error.HTTPError as e:
            if e.code == 429 or e.code == 503 or e.code == 403:
                print('Connection failed. Retrying...')
                time.sleep(random.randint(10, 20))
            else:
                raise e

    json_data = json.loads(response.read().decode())
    get_children = json_data[1]['data']['children'][1:]

    for reply in get_children:
        scrap_messages = reply['data'].get('body', None)
        if scrap_messages:
            secondaryParent.append(scrap_messages)

    time.sleep(random.randint(10, 20))
    print(len(secondaryParent))
    logData()


def logData():
    conn = psycopg2.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('USER')} "
                            f"password={os.environ.get('PASSWORD')} port={os.environ.get('PORT')} host={os.environ.get('HOST')}")
    cur = conn.cursor()

    for message in secondaryParent:
        message = re.sub(r"u/[^ ]+", "", message)
        if message:
            cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s', (message,))
            rows = cur.fetchall()
            if not rows:
                cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)', (message, "Reddit"))

    conn.commit()
    secondaryParent.clear()


while True:
    crawl()
    time.sleep(random.randint(30, 60))
