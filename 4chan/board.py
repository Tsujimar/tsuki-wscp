import re
import sys
from bs4 import BeautifulSoup
from urllib import request, error


def crawler():
    # board = sys.argv[2]
    boards = ['a', 'c', 'w', 'm', 'cgl', 'cm', 'lgbt', '3', 'adv', 'an', 'biz', 'cgl', 'ck', 'co', 'diy', 'fa', 'fit', 'gd', 'his', 'int', 'jp', 'lit', 'mlp', 'mu', 'n', 'news', 'out', 'po', 'pw', 'qst', 'sci', 'sp', 'tg', 'toy', 'trv', 'tv', 'vp', 'vt', 'wsg', 'wsr', 'x', 'xs']
    count = 0
    while count != 11:
        for board in boards:
            try:
                url = f'https://boards.4channel.org/{board}/{count}'
                response = request.urlopen(url)
                soup = BeautifulSoup(response, 'html.parser')
                main_content = soup.find_all('div', id=re.compile("t"))
                for i in range(len(main_content)):
                    head_line = main_content[i].find('span', attrs={'data-tip-cb': True})
                    post_message = main_content[i].find('blockquote', class_="postMessage")
                    if head_line is not None and post_message is not None:
                        print(head_line.text, post_message.text)
                count += 1
            except error.HTTPError as e:
                if e.code == 404:
                    count = 2


crawler()
