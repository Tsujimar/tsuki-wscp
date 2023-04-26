import re
from bs4 import BeautifulSoup
from urllib import request, error
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import psycopg2
from psycopg2 import OperationalError
import os
from sys import exit

os.system("")


class style():
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'


def crawler(delay, is_nsfw):
    try:
        conn = psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASSWORD"],
            port=os.environ["PG_PORT"],
            host=os.environ["PG_HOST"]
        )
        cur = conn.cursor()
        driver = webdriver.Firefox()

        sfw_boards = ['a', 'c', 'w', 'm', 'cgl', 'cm', 'lgbt', '3', 'adv', 'an', 'biz', 'cgl', 'ck', 'co', 'diy', 'fa',
                      'fit', 'gd',
                      'his', 'int', 'jp', 'lit', 'mlp', 'mu', 'n', 'news', 'out', 'po', 'pw', 'qst', 'sci', 'sp', 'tg',
                      'toy', 'trv',
                      'tv', 'vp', 'vt', 'wsg', 'wsr', 'x', 'xs']
        nsfw_boards = ["3", "a", "aco", "adv", "an", "asp", "b", "bant", "biz", "c", "cgl", "ck", "cm", "co", "d",
                       "diy", "e",
                       "f", "fa", "fit", "g", "gd", "gif", "h", "hc", "his", "hm", "hr", "i", "ic", "int", "jp", "k",
                       "lgbt",
                       "lit", "m", "mlp", "mu", "n", "news", "o", "out", "p", "po", "pol", "qa", "qst", "r", "r9k", "s",
                       "s4s",
                       "sci", "soc", "sp", "t", "tg", "toy", "trash", "trv", "tv", "u", "v", "vg", "vip", "vp", "vr",
                       "vrpg",
                       "vst", "w", "wg", "wsg", "wsr", "x", "y"]
        if is_nsfw:
            default_boards = nsfw_boards
        else:
            default_boards = sfw_boards

        for board in default_boards:
            count = 0

            def spider(count):
                while count != 11:
                    # Scrape posts
                    url = f'https://boards.4channel.org/{board}/{count}'
                    response = request.urlopen(url)
                    soup = BeautifulSoup(response, 'html.parser')
                    main_content = soup.find_all('div', id=re.compile("t"))
                    for i in range(len(main_content)):
                        post_message = main_content[i].find('blockquote', class_="postMessage")
                        if post_message is not None:
                            pm_t = post_message.get_text()
                            cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s',
                                        (pm_t,))
                            rows = cur.fetchall()
                            if not rows:
                                print(style.YELLOW + "[4Chan]", end='')
                                print(style.GREEN + "Added", end=' ')
                                print(style.RESET + pm_t)
                                cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)',
                                            (pm_t, "4Chan"))
                        conn.commit()
                    # Scrape comments
                    driver.get(url)
                    toggle_buttons = WebDriverWait(driver, delay).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-cmd='expand']"))
                    )
                    for toggle_button in toggle_buttons:
                        toggle_button.click()
                        WebDriverWait(driver, delay).until(
                            EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "[src='//s.4cdn.org/image/buttons/burichan/post_expand_minus.png']"))
                        )
                        html = driver.page_source
                        soup = BeautifulSoup(html, "html.parser")
                        comments = soup.find_all("div", class_="postContainer replyContainer rExpanded")
                        for comment in comments:
                            comment = comment.find("blockquote", class_="postMessage")
                            refurnished = comment.get_text()
                            new_text = re.sub(
                                r"No.\d{2,}▶|>>\d{2,}|File:.*.(jpg|png|webm|gif)|\d{2}/\d{2}/\d{2}|(.*\w)\d."
                                r"*(JPG|PNG|WEBM|GIF)|\b\w+\s\(\w{2,}\)\d{2}:\d{2}:\d{2}\b|.*(OP).|>", "", refurnished)
                            if len(new_text) != 0:
                                cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s', (new_text,))
                                rows = cur.fetchall()
                                if not rows:
                                    print(style.YELLOW + "[4Chan]", end='')
                                    print(style.GREEN + "Added", end=' ')
                                    print(style.RESET + new_text)
                                    cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)',
                                                (new_text, "4Chan"))
                            conn.commit()
                    count += 1

            spider(count)
    except Exception as e:
        if type(e) == KeyError:
            print(style.YELLOW + "[4Chan]", end='')
            print(style.RED + "DB service inactive")
            exit()
        elif type(e) == OperationalError:
            print(style.YELLOW + "[4Chan]", end='')
            print(style.RED + "Missing or wrong DB credentials.")
            exit()
        elif type(e) == WebDriverException:
            print(style.YELLOW + "[4Chan]", end='')
            print(style.RED + "Firefox developer browser was not found.")
            exit()
        elif type(e) == error.HTTPError:
            if e.code == 404:
                count = 2
                spider(count)
        elif type(e) == WebDriverException:
            count = 2
            spider(count)


def call_crawler(delay, is_nsfw):
    print("board.py loaded successfully")
    while True:
        crawler(delay, is_nsfw)