#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import requests
import yaml
import pandas as pd
import traceback
from datetime import datetime
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import tldextract
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
from libs.logger import logger
from libs.regex import file, find_ioc, is_valid_ip
from libs.timer import SimpleTimer
from utils import tree, tree2list, cur_date, writer
from paths import DUMP_HOME


headers = {
    # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    # 'Accept-Encoding': 'gzip, deflate, br',
    # 'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    # 'Host': 'www.ncut.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
}
WORK_HOME = os.path.dirname(__file__)


class NCUTCrawler(object):

    def __init__(self):
        self._load_conf()
        #
        self.site = ''
        self.urls = tree()
        self.all_urls = dict()
        self.broken_urls = dict()
        self.session = requests.session()
        self.session.headers = headers
        #
        _timeout = self.cfg.get('timeout', 1)
        self.timeout = (_timeout, _timeout * 2)   # (时间,次数)
        self.timer = SimpleTimer(300, 300, self.dump2csv)   # 每5分钟输出一次结果
        self.timer.daemon = True
        self.timer.start()
        #
        with open(os.path.join(WORK_HOME, 'white_domain.txt'), encoding='utf-8') as f:
            self.white_domain = set([line.strip('\r\n ').lower() for line in f.readlines()])
        with open(os.path.join(WORK_HOME, 'white_html.txt'), encoding='utf-8') as f:
            self.white_domain.union(set([line.strip('\r\n ').lower() for line in f.readlines()]))

    def _load_conf(self):
        conf_path = os.path.join(WORK_HOME, 'ncut.yaml')
        with open(conf_path, encoding='utf-8') as f:
            self.cfg = yaml.load(f, Loader=yaml.FullLoader)

        def _compile_regex(wb_type):
            wblist = self.cfg.get(wb_type)
            if wblist:
                regex_fuzzy = regex_precise = ''                    # 前缀模糊匹配/精确匹配
                re_items_fuzzy, re_items_precise = list(), list()   # 前缀模糊匹配/精确匹配
                suffix = [s if s.startswith('.') else '.' + s for s in wblist.get('suffix', list())]
                re_items_fuzzy.extend([s.replace('.', '\.') for s in suffix])
                domain = wblist.get('domain')
                if domain:
                    re_items_precise.extend(domain)
                    domain = [s if s.startswith('.') else '.' + s for s in domain]
                    re_items_fuzzy.extend([s.replace('.', '\.') for s in domain])
                if len(re_items_fuzzy) > 0:
                    regex_fuzzy = '.*(%s)' % '|'.join(re_items_fuzzy)

                re_items_precise.extend([s.replace('.', '\.') for s in wblist.get('host', list())])
                if len(re_items_precise) > 0:
                    regex_precise = '(%s)' % '|'.join(re_items_precise)
                if regex_fuzzy and regex_precise:
                    return re.compile(r'^(%s|%s)$' % (regex_fuzzy, regex_precise))
                elif regex_fuzzy:
                    return re.compile(r'%s$' % regex_fuzzy)
                elif regex_precise:
                    return re.compile(r'%s$' % regex_precise)
                return None

        self.white_urls = set(self.cfg.get('whitelist').get('url', list()))
        self.whitelist = _compile_regex('whitelist')
        self.blacklist = _compile_regex('blacklist')
        # EE5297BCA67674A9E58C883A99E_5DB0C66B_8080.zip?e=.zip
        # 3AB878FCFCD55264A6C314053C7_6D1D3370_18FA1A5F.mov?e=.mov
        # AdvancedSearch.do?method
        self._whitelist = re.compile(r'\w+\.(zip|mov|do)\?', re.I)

    def filter_domain(self, url):
        if self._whitelist.match(url) or url in self.white_urls:
            return ''
        ext = tldextract.extract(url)
        registered_domain = ext.registered_domain.lower()
        full_domain = ext.subdomain.lower() + '.' + registered_domain
        # 1. 优先过滤html函数、属性等白名单
        if registered_domain in self.white_domain or full_domain in self.white_domain:
            return ''
        # 2. 匹配黑名单规则
        if self.blacklist is not None and self.blacklist.match(full_domain):
            return registered_domain
        # 3. 最后匹配白名单规则
        if self.whitelist is not None and self.whitelist.match(full_domain):
            return ''
        return registered_domain

    def abspath(self, url):
        """
        获取绝对路径URL
        将相对路径URL转成绝对路径URL,避免同一URL被重复爬取
        """
        if "#" in url:
            # 移除页面内部定位符井号#,其实是同一个链接
            url = url[0:url.rfind('#')]
        while '/./' in url:
            url = url.replace('/./', '/')
        while '/../' in url:
            while re.search(r'%s/\.\./' % self.site, url):
                # 如果/../前是目标网站,则直接移除/../
                url = re.sub(r'%s/\.\.' % self.site, self.site, url)
            url = re.sub(r'[^/]+/\.\./', '', url)
        return url

    def scrape(self, start_url, path_limit=''):
        """
        执行爬取&提取页面url操作
        """
        new_urls = deque([start_url])
        # 保存所有URL的来源
        self.all_urls = dict()  # key: url, value: 该url的来源地址
        self.all_urls[start_url] = start_url

        while len(new_urls):
            url = new_urls.popleft()
            try:
                resp = self.session.get(url, timeout=self.timeout)
                logger.info('GET %s %s' % (url, resp.status_code))
                # https://stackoverflow.com/questions/20475552/python-requests-library-redirect-new-url
                # 如果发生重定向,更新URL,避免提取页面href后拼接错误新URL(大量404)
                if resp.history:
                    logger.info('!RedirectTo: %s' % resp.url)
                    self.all_urls[url] = '302'
                    url = self.abspath(resp.url)      # 更新重定向后的URL
                if 400 <= resp.status_code < 500:
                    logger.info('!From: %s ' % self.all_urls.get(url))
            # except (MissingSchema, InvalidURL, InvalidSchema, ConnectionError, ReadTimeout) as e:
            except Exception as e:
                logger.error('GET %s %s' % (url, e))
                self.broken_urls[url] = self.all_urls.get(url, '')
                continue
            # 提取url site和url路径
            parts = urlsplit(url)
            site = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url
            # 解析HTML页面
            soup = BeautifulSoup(resp.text, "lxml")   # soup = BeautifulSoup(response.text, "html.parser")
            yield url, resp.text
            # 提取页面内容里的URL
            links = soup.find_all('a')
            for link in links:
                new_url = ''
                # 从<a>标签中提取href
                href = link.attrs["href"] if "href" in link.attrs else ''
                if href.startswith("#") or href.startswith('javascript:'):
                    continue
                if href.startswith("http://") or href.startswith("https://"):
                    new_url = href
                elif href.startswith("/"):
                    new_url = site + href
                else:
                    new_url = path + href
                # 过滤图片、文档、视频音频等文件链接
                if file.match(new_url):
                    continue
                new_url = self.abspath(new_url)
                # 限制URL
                if path_limit and path_limit not in new_url:
                    continue
                if new_url and new_url not in self.all_urls:
                    self.all_urls[new_url] = url  # 保存该new_url的来源地址
                    new_urls.append(new_url)

    def dump2csv(self):
        dump_time = datetime.now().strftime('%Y%m%d')
        df = pd.DataFrame(tree2list(self.urls), columns=['url', 'url_in', 'domain', 'timestamp'])
        with pd.ExcelWriter(os.path.join(DUMP_HOME, 'nuct_urls.%s.xlsx' % dump_time)) as fout:
            df.to_excel(fout, sheet_name='all_urls')
            df[['url_in']].groupby(['url_in'])['url_in']. \
                count(). \
                reset_index(name='count'). \
                sort_values(['count'], ascending=False). \
                to_excel(fout, sheet_name='url_in', index=False)
            df[['domain']].groupby(['domain'])['domain']. \
                count(). \
                reset_index(name='count'). \
                sort_values(['count'], ascending=False). \
                to_excel(fout, sheet_name='domain', index=False)
        # df.to_csv(os.path.join(DATA_HOME, 'nuct_urls.%s.csv' % dump_time))
        writer(os.path.join(DUMP_HOME, 'all_urls.%s.txt' % dump_time), sorted(self.all_urls.keys()))
        writer(os.path.join(DUMP_HOME, 'broken_urls.%s.txt' % dump_time), sorted(self.broken_urls.keys()))
        logger.info('Dump success. Total urls:%d, Broken urls: %d' % (len(self.urls), len(self.broken_urls)))

    def main(self):
        start_url = self.cfg.get('start_url', 'https://www.ncut.edu.cn/')
        self.site = tldextract.extract(start_url).registered_domain.lower()
        path_limit = self.site + '/'  # 限制只爬取同站网页
        existed_ioc = tree()
        for url, html_text in self.scrape(start_url, path_limit=path_limit):
            candidates = find_ioc(html_text)
            for ioc in candidates:
                # 去重当前URL页面里已提取出的链接
                if ioc in existed_ioc[url]:
                    continue
                existed_ioc[url][ioc] = ioc
                if is_valid_ip(ioc):
                    logger.info('>> ' + ioc)
                    self.urls[url][ioc][ioc] = cur_date()
                else:
                    domain = self.filter_domain(ioc)
                    if domain:
                        logger.info('>> ' + ioc)
                        self.urls[url][ioc][domain] = cur_date()


if __name__ == '__main__':
    crawler = NCUTCrawler()
    try:
        crawler.main()
        crawler.dump2csv()
    except KeyboardInterrupt:
        crawler.dump2csv()
    except:
        logger.error(traceback.format_exc())
        crawler.dump2csv()

