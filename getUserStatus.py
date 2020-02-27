#!/usr/bin/env python3
# coding: utf-8

import requests
import random
import re
import time
import subprocess
from bs4 import BeautifulSoup
from urllib import parse
from datetime import datetime


def run_command(command):
    return subprocess.getoutput(command)


def request(url):
    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
    ]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': user_agents[random.randint(0, len(user_agents) - 1)],
        'Referer': 'http://web.humoruniv.com/board/humor/list.html?asdfasdfasasdf',
    }
    result = subprocess.run(['curl', '--user-agent', headers['User-Agent'], url, '-s', '-H', 'Accept-Encoding: gzip, deflate'], stdout=subprocess.PIPE, encoding='cp949')
    return result.stdout

def get_soup(url):
    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41',
    ]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': user_agents[random.randint(0, len(user_agents) - 1)],
        'Referer': 'http://web.humoruniv.com/board/humor/',
    }
    while True:
        r = request(url)
        # r.encoding = 'euc-kr'
        if r.find('시스템 과부하 혹은 지나친 접속이 감지되어 서비스가 지연되고 있습니다. 잠시 기다리신 후에 다시 시도해 주세요.') > -1:
            print('웃긴대학에서 시스템 과부화를 감지하였습니다. 10초 뒤에 다시 시작합니다.')
            time.sleep(10)
        else:
            break
    return BeautifulSoup(r, 'lxml')


class User:
    comments = []
    total_comments = 0
    end_page = 0
    progress_rate = 0           # 진행율

    def __init__(self, nickname):
        self.comment_process_end = False
        self.nickname = nickname
        self.euc_kr_nickname = self.nickname.encode('euc-kr')
        self.get_page()
        self.get_all_comments()

    # 사용자의 댓글 리스트에서 최대 페이지를 가져옴
    def get_page(self):
        soup = get_soup(self.set_url())
        tmp = soup.select('div.page table td > span')[0].text.replace(',', '')
        [self.total_comments, self.end_page] = map(int, re.findall('\d+', tmp))

    def set_url(self, page=1):
        url = "http://web.humoruniv.com/board/humor/comment_search.html?sort=mtime&searchday=all&sk={0}&page={1}"
        url_encoded_nickname = parse.quote(self.euc_kr_nickname)
        return url.format(url_encoded_nickname, page)

    def get_user_comment_list_from_page(self, page, day_limit=7):

        if self.comment_process_end is True:
            return None

        comments = []
        soup = get_soup(self.set_url(page))
        # print(self.set_url(page))         # for debugging
        body = soup.find('div', class_='body_main')

        # # for debugging
        if body is None:
            print(soup.prettify())
        tr_list = body.find_all('tr')
        for tr in tr_list:
            span_nick = tr.find('span', class_='hu_nick_txt')
            if span_nick is not None and span_nick.get_text() == self.nickname:

                # 댓글을 남긴 게시물에는 반대를 표현할 때 not_ok class를 불러오지 않는 점을 이용하여 댓글과 게시물을 구분한다.
                if tr.find('span', class_='not_ok') is not None:

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

                    # 지정한 일 수보다 오래된 댓글이면 저장하지 않음
                    if (datetime.now() - comment_time).days > day_limit:
                        self.comment_process_end = True
                        return comments

        return comments

    def get_all_comments(self):
        start_time = datetime.now()
        for page in range(1, self.end_page + 1):
            self.progress_rate = page / self.end_page
            print("진행율 {:.1%}".format(self.progress_rate))
            for comment in self.get_user_comment_list_from_page(page):
                if comment is not None:
                    self.comments.append(comment)
        end_time = datetime.now()
        execution_time = end_time - start_time
        print('총 걸린 시간:', execution_time)

    def get_recommendation_average(self):
        recommendation_sum = 0
        for comment in self.comments:
            recommendation_sum += comment['recommendation']
        return recommendation_sum / len(self.comments)


if __name__ == '__main__':
    u = User('송어회')
    print(u.get_recommendation_average())