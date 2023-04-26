import re
from urllib import error
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException, TimeoutException
import psycopg2
from psycopg2 import OperationalError
import os
from sys import exit
import time

os.system("")


class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'


def stage_final(conn, data):
    try:
        db = conn.cursor()
        for string in data:
            if len(string) != 0:
                db.execute('SELECT * FROM "wscp_data" WHERE "message" = %s', (string,))
                rows = db.fetchall()
                if not rows:
                    print(style.YELLOW + "[Twitter]", end='')
                    print(style.GREEN + "Added", end=' ')
                    print(style.RESET + string)
                    db.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)',
                               (string, "Twitter"))
            conn.commit()
    except Exception:
        print(style.YELLOW + "[Twitter]", end='')
        print(style.GREEN + "A critical error occurred while sending data to db. Please check your services." + style.RESET)
        exit()


def call_url(tweet, driver, replies_set):
    href_link = tweet.get_attribute('href')
    cleaned = re.compile(r'/analytics$')
    new_url = cleaned.sub('', href_link)
    if "status" in new_url:
        print(style.YELLOW + "[Twitter]", end='')
        print(style.GREEN + f"Harvesting from {new_url}" + style.RESET)
        driver.execute_script("window.open('{}', '_blank');".format(new_url))
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(5)
        get_origin_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div/div/div/main/div/div/div/div/div/'
                           'section/div/div/div/div/div/article/div/div/div/div/div/div/span'))
        )
        replies_set.add(get_origin_header.text)
        return replies_set


ended_successfully = True
try_count = 1


def tweet_worker(driver, tweet, replies_set, replies_min, tweets_set, accept):
    try:
        check_refresh = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div/div/div/main/div/div/div/div/div/div/div'))
        )
        if check_refresh.text == 'Refresh':
            check_refresh.click()
    except Exception:
        pass
    href_link = tweet.get_attribute('href')
    cleaned = re.compile(r'/analytics$')
    new_url = cleaned.sub('', href_link)
    if "status" in new_url:
        call_url(tweet, driver, replies_set)
        get_replies(driver, replies_min, replies_set, accept)
        replies_set.add("plain")
        num_tabs = len(driver.window_handles)
        if num_tabs <= 2:
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
        tweets_set.add(tweet)
    return replies_set


def get_replies(driver, replies_min, replies_set, accept):
    if accept is True:
        while True:
            last_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            try:
                check_load = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div/main/div/div/'
                                                          'div/div/div/section/div/div/div/div/div/div/div/div/span | '
                                                          '/html/body/div/div/div/div/main/div/div/div/div/div/section/div/div/div/div/div/article/div/div/div/div/div/div/div/div/span/span'))
                )
                check_load.click()
                time.sleep(3)
                new_height = driver.execute_script("return document.body.scrollHeight")
            except TimeoutException:
                pass

            if new_height == last_height:
                break
            if replies_min != 0:
                replies = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '/html/body/div/div/div/div/main/div/div/'
                                   'div/div/div/section/div/div/div/div/div/article/'
                                   'div/div/div/div/div/div/span'))
                )
                for reply in replies:
                    plain = reply.get_attribute('textContent').strip()
                    replies_set.add(plain)
    return replies_set


def tweet_handler(pure_tag, replies_min, driver, db):
    global ended_successfully
    global try_count
    time.sleep(5)
    print(style.YELLOW + "[Twitter]", end='')
    print(style.GREEN + f"Operation for #{pure_tag}'s top posts" + style.RESET)
    url_sub = f'https://twitter.com/search?q={pure_tag} min_replies%3A{replies_min}&src=typed_query&f=top'
    if replies_min == 0:
        print(style.YELLOW + "[Twitter]", end='')
        print(style.GREEN + f"No more tweets with high replies found. Fetching empty tweets..." + style.RESET)
        url_sub = f'https://twitter.com/search?q={pure_tag}&src=typed_query&f=top'
    driver.get(url_sub)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(5)
    try:
        check_refresh = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/main/div/div/div/div/div/div/div'))
        )
        if check_refresh.text == 'Refresh':
            check_refresh.click()
    except Exception:
        pass
    try:
        replies_set = set()
        tweets_set = set()
        while True:
            last_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            new_height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(5)
            if new_height == last_height:
                break
            tweets = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH,
                                                     '/html/body/div/div/div/div/main/div/div/div/div/div/div/div/section/'
                                                     'div/div/div/div/div/article/div/div/div/div/div/div/div/a'))
            )
            for tweet in tweets:
                try:
                    if replies_min == 0:
                        replies_set = tweet_worker(driver, tweet, replies_set, replies_min, tweets_set, False)
                    else:
                        replies_set = tweet_worker(driver, tweet, replies_set, replies_min, tweets_set, True)
                except Exception as e:
                    print(style.YELLOW + "[Twitter]", end='')
                    print(
                        style.RED + f"An unexpected error occurred during post fetching. Possibly an error communicating with server, continuing after 30 seconds... " + style.RESET)
                    time.sleep(30)
                    replies_set = tweet_worker(driver, tweet, replies_set, replies_min, tweets_set, True)
        ended_successfully = True
        if ended_successfully is True:
            print(style.YELLOW + "[Twitter]", end='')
            print(
                style.GREEN + f"Finished harvesting top posts from #{pure_tag} successfully. Starting all tweet origin harvest..." + style.RESET)
            secondary_url = f'https://twitter.com/search?q={pure_tag}&src=typed_query&f=top'
            driver.get(secondary_url)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)
            while True:
                last_height = driver.execute_script("return document.body.scrollHeight")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                time.sleep(5)
                tweets = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH,
                                                         '/html/body/div/div/div/div/main/div/div/div/div/div/div/div/section/'
                                                         'div/div/div/div/div/article/div/div/div/div/div/div/div/a'))
                )
                for tweet in tweets:
                    replies_set = tweet_worker(driver, tweet, replies_set, replies_min, tweets_set, False)
        # End secondary task on True
        replies_collection = list(replies_set)
        if len(replies_collection) == 0:
            raise TimeoutException
        print(style.YELLOW + "[Twitter]", end='')
        print(
            style.GREEN + f"Process for #{pure_tag} finished. Retrieved {len(replies_collection)} data rows." + style.RESET)
        stage_final(db, replies_collection)
        tweets_collection = list(tweets_set)
        return tweets_collection
    except Exception as e:
        if type(e) == TimeoutException:
            print(style.YELLOW + "[Twitter]", end='')
            print(style.RED + f"No tweets found for #{pure_tag} with minimum of 5 replies, moving on...", end=' ')
            print(f"retrying with no minimum..." + style.RESET)
            time.sleep(5)
            replies_min = 0
            ended_successfully = False
            if try_count == 2:
                try_count = 1
                return None
            else:
                try_count += 1
            driver.close()
            driver.switch_to.window(driver.window_handles[-1])
            stage_final(db, replies_collection)
            return tweet_handler(pure_tag, replies_min, driver, db)
            # return None
        else:
            print(style.YELLOW + "[Twitter]", end='')
            print(
                style.RED + f"An unexpected error occurred while harvesting posts. Skipping #{pure_tag}..." + style.RESET)
            replies_collection = list(replies_set)
            stage_final(db, replies_collection)
            return None


def spidercrawler(delay):
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASSWORD"],
            port=os.environ["PG_PORT"],
            host=os.environ["PG_HOST"]
        )
        driver = webdriver.Firefox()
        driver.set_window_size(800, 1080)
        try:
            url = f'https://twitter.com/i/trends'
            driver.get(url)
            try:
                xpath_expr = "/html/body/div/div/div/div/main/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div/span" \
                             "| /html/body/div/div/div/div/main/div/div/div/div/div/div/section/div/div/div/div/div/div/div/div/span/span"
                time.sleep(5)
                trends = WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.XPATH, xpath_expr))
                )
            except Exception as e:
                if type(e) == StaleElementReferenceException:
                    print(style.YELLOW + "[Twitter]", end='')
                    print(style.RED + "Element reference error, retrying in 5 seconds...")
                    driver.quit()
                    time.sleep(5)
                    spidercrawler(delay)
                else:
                    print(style.YELLOW + "[Twitter]", end='')
                    print(
                        style.RED + "Twitter seems to be down for now. Please check https://downdetector.com/status/twitter/")
                    exit()
            revised = []
            for trend in trends:
                tag = trend.text
                if "#" in tag:
                    new_tag = str(tag).replace("#", '')
                    if len(new_tag) > 1:
                        revised.append(new_tag)
                elif "Tweets" not in tag:
                    revised.append(tag)
            unique = list(set(revised))
            for pure_tag in unique:
                replies_min = 5
                url_sub = f'https://twitter.com/search?q={pure_tag} min_replies%3A{replies_min}&src=typed_query&f=top'
                driver.get(url_sub)
                # Begin Login redirect
                time.sleep(5)
                current_landing = driver.execute_script("return window.location.href;")
                if current_landing == "https://twitter.com/i/flow/login":
                    peu_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "text"))
                    )
                    try:
                        peu_field.send_keys(os.environ["TWITTER_PEU"])
                    except KeyError:
                        print(style.YELLOW + "[Twitter]", end='')
                        print(style.RED + "Missing Twitter credentials.")
                        exit()
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/"
                                       "div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]"))
                    )
                    next_button.click()
                    password_field = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.NAME, "password"))
                    )
                    try:
                        password_field.send_keys(os.environ["TWITTER_PASSWORD"])
                    except KeyError:
                        print(style.YELLOW + "[Twitter]", end='')
                        print(style.RED + "Missing Twitter credentials.")
                        exit()
                    final_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH,
                                                    "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/"
                                                    "div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div"))
                    )
                    final_button.click()
                    time.sleep(5)
                # End login redirect
                tweet_handler(pure_tag, replies_min, driver, conn)
        except error.HTTPError as e:
            print(style.YELLOW + "[Twitter]", end='')
            print(style.RED + "An HTTP error occurred, retrying in 5 seconds...")
            time.sleep(5)
            spidercrawler(delay)

    except Exception as e:
        if type(e) == KeyError:
            print(style.YELLOW + "[Twitter]", end='')
            print(style.RED + "DB service inactive")
            exit()
        elif type(e) == OperationalError:
            print(style.YELLOW + "[Twitter]", end='')
            print(style.RED + "Missing or wrong DB credentials.")
            exit()
        elif type(e) == WebDriverException:
            print(style.YELLOW + "[Twitter]", end='')
            print(style.RED + "Firefox developer browser was not found.")
            exit()


def call_spidermusk(delay=30):
    print(style.RED + "[BETA] " + style.RESET + "spidermusk loaded successfully")
    while True:
        spidercrawler(delay)
