# -*- coding: utf-8 -*-

import requests
import datetime
from bs4 import BeautifulSoup
from getContentInfo import Content

class Worker:
    period = 60 * 60        # 해당 시간 내의 게시물 로드

    def __init__(self, period):
        self.period = period

    def get_soup(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
        }
        r = requests.get(url, headers=headers)
        r.encoding = 'euc-kr'
        return BeautifulSoup(r.text, 'lxml')

    def get_contents_list(self, table):
        i = 0
        break_ = False

        while True:
            soup = self.get_soup('http://web.humoruniv.com/board/humor/list.html?table={0}&pg={1}'.format(table, i))
            tr_list = soup.findAll('tr', id=lambda x: x and x.startswith('li_chk_{0}-'.format(table)))
            for tr in tr_list:
                tr_id = int(tr.get('id').replace('li_chk_{0}-'.format(table), ''))
                print(tr_id)
                # c = Content(table, tr_id)
                datetime_ = '{0} {1}'.format(tr.find('span', class_='w_date').get_text(),
                                             tr.find('span', class_='w_time').get_text())
                post_datetime = datetime.datetime.strptime(datetime_, '%Y-%m-%d %H:%M')
                post_duration = datetime.datetime.now() - post_datetime

                # 게시글을 작성한지 일주일 이상이 지남
                if post_duration.days > 7:
                    print('http://web.humoruniv.com/board/humor/list.html?table={0}&pg={1}'.format(table, i))
                    break_ = True
                    break

                else:
                    i += 1

            if break_ is True:
                break


if __name__ == '__main__':
    w = Worker(60 * 60)
    w.get_contents_list('pdswait')
