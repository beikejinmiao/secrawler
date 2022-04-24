#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import requests
from docx import Document

# with open('test.pptx', 'rb') as fopen:
#     for line in fopen.readlines():
#         texts = re.findall(rb'[\x20-\x7e]+', line)
#         print('>>', line)
#         for t in texts:
#             print(str(t, encoding='utf-8'))


# doc = Document('test.docx')
# for p in doc.paragraphs:
#     print('>>', p.text)
#

default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
}
resp = requests.get('http://www.btbu.edu.cn/eapdomain/static/cmsfiles/pim/File/20090914095604.doc', allow_redirects=True, headers=default_headers)
with open('xxx.doc', 'wb') as fopen:
    fopen.write(resp.content)
print(resp.status_code)
print(resp.url)
print(resp.history)
print(str(resp.content, encoding='utf-8'))

# import wget
# url = 'http://www.btbu.edu.cn/eapdomain/static/cmsfiles/pim/File/20090914095604.doc'
# filename = wget.download(url)
