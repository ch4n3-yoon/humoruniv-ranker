# -*- coding: utf-8 -*-

import requests
import random
import string
from bs4 import BeautifulSoup


class Content:
    table = ''              # 게시판
    number = 0              # 글 고유번호
    content_url = ''        # 글 URL
    soup = ''               # BeautifulSoup 객체
    writer = ''             # 작성자
    recommendation = 0      # 추천수
    opposition = 0          # 반대 수
    comments = 0            # 댓글 수
    title = ''              # 글 제목

    def __init__(self, table, number):
        self.table = table
        self.number = number
        self.content_url = 'http://web.humoruniv.com/board/humor/read.html?table={0}&number={1}'.format(table, number)
        self.soup = BeautifulSoup(self.get_raw_content(), 'lxml')
        self.parse()

    def parse(self):
        self.get_writer()
        self.get_recommendation()
        self.get_opposition()
        self.get_comments()
        self.get_title()

    def get_raw_content(self):
        user_agents = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
        ]

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': user_agents[random.randint(0, len(user_agents) - 1)],
            'Referer': 'http://web.humoruniv.com/board/humor/list.html?table=com',
        }
        r = requests.get(self.content_url, headers=headers)
        r.encoding = 'euc-kr'
        return r.text

    def get_writer(self):
        nicks = self.soup.findAll('span', class_='hu_nick_txt')
        self.writer = str(nicks[0].string)

    def get_recommendation(self):
        self.recommendation = int(self.soup.find('span', id='ok_div').get_text())

    def get_opposition(self):
        self.opposition = int(self.soup.find('span', class_='b').get_text())

    def get_comments(self):
        self.comments = int(self.soup.find('span', class_='re').get_text())

    def get_title(self):
        self.title = self.soup.find('span', id='ai_cm_title').get_text()


if __name__ == '__main__':
    c = Content('pds', 936490)
    print(vars(c))
