#!/usr/bin/env python3
# coding: utf-8

import requests
import random
import re
from bs4 import BeautifulSoup
from urllib import parse
from datetime import datetime


def get_soup(url):
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
    r = requests.get(url, headers=headers)
    r.encoding = 'euc-kr'
    return BeautifulSoup(r.text, 'lxml')


class User:
    comments = []
    total_comments = 0
    end_page = 0

    def __init__(self, nickname):
        self.nickname = nickname
        self.euc_kr_nickname = self.nickname.encode('euc-kr')
        self.get_page()

    # 사용자의 댓글 리스트에서 최대 페이지를 가져옴
    def get_page(self):
        soup = get_soup(self.set_url())
        tmp = soup.select('div.page table td > span')[0].text
        [self.total_comments, self.end_page] = map(int, re.findall('\d+', tmp))

    def set_url(self, page=1):
        url = "http://web.humoruniv.com/board/humor/comment_search.html?sort=mtime&searchday=all&sk={0}&page={1}"
        url_encoded_nickname = parse.quote(self.euc_kr_nickname)
        return url.format(url_encoded_nickname, page)

    def get_user_comment_list_from_page(self, page):
        comments = []
        soup = get_soup(self.set_url(page))
        body = soup.find('div', class_='body_main')
        tr_list = body.find_all('tr')
        for tr in tr_list:
            span_nick = tr.find('span', class_='hu_nick_txt')
            if span_nick is not None and span_nick.get_text() == self.nickname:

                # 댓글을 남긴 게시물에는 반대를 표현할 때 not_ok class를 불러오지 않는 점을 이용하여 댓글과 게시물을 구분한다.
                if tr.find('span', class_='not_ok') is not None:

                    # 추천 / 및 반대 파싱
                    recommendation = int(tr.find('span', class_='ok').text)
                    opposition = int(tr.find('span', class_='not_ok').text)

                    comment = tr.find('span', class_='comment').text

                    datetime_ = tr.find('span', class_='date').text
                    comment_time = datetime.strptime(datetime_, '%Y-%m-%d %H:%M:%S')

                    comments.append({
                        'comment': comment,
                        'recommendation': recommendation,
                        'opposition': opposition,
                        'comment_time': comment_time,
                    })

        return comments

    def get_all_comments(self):
        for page in range(1, self.end_page + 1):
            for comment in self.get_user_comment_list_from_page(page):
                self.comments.append(comment)


if __name__ == '__main__':
    u = User('니가아는그애')
    u.get_all_comments()