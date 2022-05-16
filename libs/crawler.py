#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import re
import requests
from urllib.parse import urlparse
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import tldextract
from libs.regex import html, common_dom
from libs.logger import logger

default_headers = {
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
}


def url_file(url):
    if url.endswith('/'):
        return ''
    url = urlparse(url).path    # 移除URL参数
    if html.match(url) or common_dom.match(url):
        return ''
    if re.match(r'.+\.\w{2,5}$', url) and not re.match(r'.+\.[\d_]+$', url):
        return os.path.basename(url)
    return ''


class Spider(object):
    def __init__(self, start_url, same_site=True, headers=None, timeout=10, ignore_file=True, hsts=False):
        self._start_url = start_url
        self.site = tldextract.extract(start_url).registered_domain.lower()
        #
        self.all_urls = dict()          # key: url, value: 该url的来源地址
        self.all_urls[start_url] = start_url
        self.broken_urls = dict()
        self.file_urls = dict()
        #
        self.session = requests.session()
        self.session.headers = headers if isinstance(headers, dict) and len(headers) > 0 else default_headers
        self.timeout = timeout
        #
        self.same_site = same_site          # 是否限制只爬取同站网页
        self.ignore_file = ignore_file      # 是否忽略文件链接
        self.hsts = hsts                    # 是否只访问HTTPS网站链接

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

    def scrape(self, path_limit=None):
        """
        执行爬取&提取页面url操作
        """
        new_urls = deque([self._start_url])
        # 保存所有URL的来源
        while len(new_urls):
            url = new_urls.popleft()
            # 处理文件链接(文件过大下载较慢,影响爬取速度)
            if self.ignore_file:
                filename = url_file(url)
                if filename:
                    self.file_urls[url] = self.all_urls.get(url)
                    yield url, filename, None
                    continue
            # 爬取正常网页
            try:
                resp = self.session.get(url, timeout=self.timeout)
                logger.info('GET %s %s' % (url, resp.status_code))
                # https://stackoverflow.com/questions/20475552/python-requests-library-redirect-new-url
                # 如果发生重定向,更新URL,避免提取页面href后拼接错误新URL(大量404)
                if resp.history:
                    logger.info('!RedirectTo: %s' % resp.url)
                    self.all_urls[url] = '302'
                    url = self.abspath(resp.url)  # 更新重定向后的URL
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
            soup = BeautifulSoup(resp.text, "lxml")  # soup = BeautifulSoup(response.text, "html.parser")
            yield url, None, resp.text
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
                # 过滤链接
                if self.filter_url(new_url):
                    continue
                new_url = self.abspath(new_url)
                # 限制URL
                if path_limit and path_limit not in new_url:
                    continue
                if self.same_site and self.site not in new_url:
                    continue
                if self.hsts and new_url.startswith('http://'):
                    new_url = 'https://' + new_url[7:]
                if new_url and new_url not in self.all_urls:
                    self.all_urls[new_url] = url  # 保存该new_url的来源地址
                    new_urls.append(new_url)

    def filter_url(self, url):
        return False

    def dump(self):
        pass

    def run(self):
        pass

