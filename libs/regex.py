#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import tldextract

ipv4 = re.compile(r"^((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)(\.((25[0-5])|(2[0-4]\d)|(1\d\d)|([1-9]\d)|\d)){3}$")
# http://stackoverflow.com/questions/9238640/how-long-can-a-tld-possibly-be
domain = re.compile(r"^([\w\-]{1,128}\.){1,255}[a-zA-Z]{2,16}$")
url = re.compile(r"^(http[s]?://.*)|(([\w\-]+\.){1,10}[a-zA-Z]{2,16}(?:\:\d+)?[/?].*)$")

# find regex
domain_find_regex = re.compile(r"(?:[\w-]+\.)+[0-9a-zA-Z]+")
http_url_find_regex = re.compile(r'http[s]?://[\w\-.:]+\w+[\w./?&=+#%-]+')
nohttp_url_find_regex = re.compile(r'(?:[\w\-]{1,128}\.){1,16}\w+(?:\:\d+)?[/?][\w./?&=+#%-]+')


# html = re.compile(r".*\.(html|htm|shtml|shtm|xhtml|asp|jsp|php)$", re.I)
file = re.compile(r".*\.("
                  r"jpg|jpeg|gif|png|ico|bmp|svg|pic|tif|tiff|psd|xcf|cdr|eps|indd|"
                  r"csv|pdf|doc|docx|xls|xlsx|xltx|ppt|pptx|vsd|vsdx|chm|odt|swf|xml|"
                  r"zip|tar|7z|rar|gz|tgz|xz|bz|bz2|exe|apk|msi|iso|bin|"
                  r"mp4|mp3|avi|mkv|flv|3gp|ts|m3u8|wav|mov|wmv|wmx|"
                  r"jar|class|rpm|deb|whl|dbf"
                  r")$", re.I)
gov_edu = re.compile(r"^([0-9a-zA-Z][0-9a-zA-Z\-]{0,62}\.){1,255}(gov|edu)(\.[a-zA-Z]{2})?")

common_suffix = {'com', 'cn', ''}


def is_valid_ip(text):
    if ipv4.match(text):
        return True
    return False


def is_valid_domain(text):
    if domain.match(text) and "." in text[-7:] and tldextract.extract(text).suffix != "":
        return True
    return False


def maybe_url(text):
    if url.match(text) and tldextract.extract(text).suffix != "":
        return True
    return False


def is_gov_edu(text):
    if gov_edu.match(text):
        return True
    return False


def find_domains(text):
    domains = set()
    for item in domain_find_regex.findall(text):
        # in general, domain suffix length less than 6.
        if "." in item[-7:] and tldextract.extract(item).suffix != "":
            domains.add(item)
    return list(domains)


def find_urls(text):
    urls = http_url_find_regex.findall(text)
    rmhttp = [re.sub("(http[s]?://)", "", url) for url in urls]
    diff = set(nohttp_url_find_regex.findall(text)) - set(rmhttp)
    urls.extend(list(diff))
    return urls


# ioc_find_regex = re.compile(r'('
#                             r'http[s]?://[\w\-.:]+\w+[\w./?&=+#%-]+|'
#                             r'(?:[\w\-]+\.){1,16}\w+(?::\d+)?[/?][\w./?&=+#%-]+|'
#                             r'\b(?<![@/])[0-9a-zA-Z](?:[\w-]+\.)+[0-9a-zA-Z]{1,8}'    tes   # 忽略邮箱和url：t@126.com, ../1235/7214.htm
#                             r')')

ioc_find_regex = re.compile(r'('
                            r'http[s]?://[\w\-.:]+\w+[\w./?&=+#%-]+|'
                            r'(?:[\w\-]+\.){1,16}\w+(?::\d+)?[/?][\w./?&=+#%-]+'
                            r')')


def is_valid_ioc(text):
    return is_valid_ip(text) or is_valid_domain(text) or maybe_url(text)


def find_ioc(text):
    return [ioc for ioc in ioc_find_regex.findall(text) if is_valid_ioc(ioc)]
