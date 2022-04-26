#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import pandas as pd
from datetime import datetime
from libs.crawler import Spider
from libs.timer import SimpleTimer
from utils import tree, tree2list, cur_date, writer
from paths import DUMP_HOME, DOWNLOADS
from modules.btbu.util import find_idcard
from modules.btbu.archive import unarchive
import traceback
from libs.logger import logger

university = 'btbu'


class BTBUCrawler(Spider):

    def __init__(self, start_url, same_site=True, headers=None, timeout=10, ignore_file=True, hsts=False):
        super().__init__(start_url,
                         same_site=same_site,
                         headers=headers,
                         timeout=timeout,
                         ignore_file=ignore_file,
                         hsts=hsts)
        self.timer = SimpleTimer(300, 300, self.dump)   # 每5分钟输出一次结果
        self.timer.daemon = True
        self.timer.start()
        #
        self.infos = tree()

    def run(self):
        existed_target = tree()
        for url, filename, html_text in self.scrape():
            if html_text is None:
                continue
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
        with pd.ExcelWriter(os.path.join(DUMP_HOME, '%s_results.%s.xlsx' % (university, dump_time))) as fout:
            df.to_excel(fout, sheet_name='all_urls')
            df[['idcard']].groupby(['idcard'])['idcard']. \
                count(). \
                reset_index(name='count'). \
                sort_values(['count'], ascending=False). \
                to_excel(fout, sheet_name='idcard', index=False)
        writer(os.path.join(DUMP_HOME, 'all_urls.%s.txt' % dump_time), sorted(self.all_urls.keys()))
        writer(os.path.join(DUMP_HOME, 'broken_urls.%s.txt' % dump_time), sorted(self.broken_urls.keys()))
        writer(os.path.join(DUMP_HOME, 'file_urls.%s.txt' % dump_time), sorted(self.file_urls.keys()))
        writer(os.path.join(DUMP_HOME, 'file_urls.%s.json' % dump_time), self.file_urls)
        logger.info('Dump success. Total urls:%d, Broken urls: %d, File urls: %d' %
                    (len(self.all_urls), len(self.broken_urls), len(self.file_urls)))


if __name__ == '__main__':
    crawler = BTBUCrawler('https://www.btbu.edu.cn/', hsts=True)
    # crawler = BTBUCrawler('http://localhost:8000/')
    try:
        crawler.run()
        crawler.dump()
    except KeyboardInterrupt:
        crawler.dump()
    except:
        logger.error(traceback.format_exc())
        crawler.dump()
