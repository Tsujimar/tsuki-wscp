import re
import sys
from bs4 import BeautifulSoup
from urllib import request, error
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()


def crawler():
    conn = psycopg2.connect(f"dbname={os.environ.get('DB_NAME')} user={os.environ.get('USER')} "
                            f"password={os.environ.get('PASSWORD')} port={os.environ.get('PORT')} host={os.environ.get('HOST')}")
    cur = conn.cursor()
    # board = sys.argv[2]
    driver = webdriver.Firefox()
    boards = ['a', 'c', 'w', 'm', 'cgl', 'cm', 'lgbt', '3', 'adv', 'an', 'biz', 'cgl', 'ck', 'co', 'diy', 'fa', 'fit',
              'gd', 'his', 'int', 'jp', 'lit', 'mlp', 'mu', 'n', 'news', 'out', 'po', 'pw', 'qst', 'sci', 'sp', 'tg',
              'toy', 'trv', 'tv', 'vp', 'vt', 'wsg', 'wsr', 'x', 'xs']
    for board in boards:
        count = 0
        while count != 11:
            try:
                # Scrape posts
                url = f'https://boards.4channel.org/{board}/{count}'
                response = request.urlopen(url)
                soup = BeautifulSoup(response, 'html.parser')
                main_content = soup.find_all('div', id=re.compile("t"))
                for i in range(len(main_content)):
                    head_line = main_content[i].find('span', attrs={'data-tip-cb': True})
                    post_message = main_content[i].find('blockquote', class_="postMessage")
                    if head_line is not None and post_message is not None:
                        hl_t = head_line.get_text()
                        pm_t = post_message.get_text()
                        print(f"Added {hl_t} and {pm_t}")
                        cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s AND "message" = %s', (hl_t, pm_t))
                        rows = cur.fetchall()
                        if not rows:
                            cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)',
                                        (hl_t, "4Chan"))
                            cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)',
                                        (pm_t, "4Chan"))
                    conn.commit()
                # Scrape comments
                driver.get(url)
                toggle_buttons = WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-cmd='expand']"))
                )
                for toggle_button in toggle_buttons:
                    toggle_button.click()
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "[src='//s.4cdn.org/image/buttons/burichan/post_expand_minus.png']"))
                    )
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    comments = soup.find_all("div", class_="postContainer replyContainer rExpanded")
                    for comment in comments:
                        refurnished = comment.get_text().split()[5:]
                        joined = " ".join(refurnished)
                        new_text = re.sub(r"No.\d{9}▶|>>\d{9}|File:.*.(jpg|png|webm|gif)|\d{2}/\d{2}/\d{2}|(.*\w)\d.*(JPG|PNG|WEBM|GIF)|\b\w+\s\(\w{3}\)\d{2}:\d{2}:\d{2}\b", "", joined)
                        if len(new_text) != 0:
                            print(f"Added {new_text}")
                            cur.execute('SELECT * FROM "wscp_data" WHERE "message" = %s', (new_text,))
                            rows = cur.fetchall()
                            if not rows:
                                cur.execute('INSERT INTO "wscp_data" ("message", "source") VALUES (%s, %s)',
                                            (new_text, "4Chan"))
                        conn.commit()
                count += 1
            except error.HTTPError as e:
                if e.code == 404:
                    count = 2
            except WebDriverException:
                count = 2


crawler()