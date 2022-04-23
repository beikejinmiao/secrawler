#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import pandas as pd
from datetime import datetime
from libs.crawler import Spider
from libs.timer import SimpleTimer
from modules.btbu.util import find_idcard
from utils import tree, tree2list, cur_date, writer
from paths import DUMP_HOME
from libs.logger import logger

university = 'btbu'


class BTBUCrawler(Spider):

    def __init__(self, start_url, same_site=True, headers=None, timeout=10):
        super().__init__(start_url, same_site=same_site, headers=headers, timeout=timeout)
        self.timer = SimpleTimer(300, 300, self.dump)   # 每5分钟输出一次结果
        self.timer.daemon = True
        self.timer.start()
        #
        self.infos = tree()

    def run(self):
        existed_target = tree()
        for url, html_text in self.scrape():
            candidates = find_idcard(html_text)
            for idcard in candidates:
                # 去重当前URL页面里已提取出的链接
                if idcard in existed_target[url]:
                    continue
                existed_target[url][idcard] = idcard
                logger.info('>> ' + idcard)
                self.infos[url][idcard] = cur_date()

    def dump(self):
        dump_time = datetime.now().strftime('%Y%m%d')
        df = pd.DataFrame(tree2list(self.infos), columns=['url', 'idcard', 'timestamp'])
        with pd.ExcelWriter(os.path.join(DUMP_HOME, '%s_urls.%s.xlsx' % (university, dump_time))) as fout:
            df.to_excel(fout, sheet_name='all_urls')
            df[['idcard']].groupby(['idcard'])['idcard']. \
                count(). \
                reset_index(name='count'). \
                sort_values(['count'], ascending=False). \
                to_excel(fout, sheet_name='idcard', index=False)
        writer(os.path.join(DUMP_HOME, 'all_urls.%s.txt' % dump_time), sorted(self.all_urls.keys()))
        writer(os.path.join(DUMP_HOME, 'broken_urls.%s.txt' % dump_time), sorted(self.broken_urls.keys()))
        logger.info('Dump success. Total urls:%d, Broken urls: %d' % (len(self.infos), len(self.broken_urls)))


