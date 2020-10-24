# -*- coding: utf-8 -*-

#
# 提取广告规则，并且只提取对全域禁止的那种规则
#

# 参考 ADB 广告规则格式：https://adblockplus.org/filters

import re
import sys
import time

import requests

rules_url = [
    # EasyList China
    # 'https://easylist-downloads.adblockplus.org/easylistchina.txt',
    # EasyList + China
    'https://easylist-downloads.adblockplus.org/easylistchina+easylist.txt',
    # 乘风 广告过滤规则
    'https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/ABP-FX.txt'
]

rule_text = ''

# contain both domains and ips
domains = []

for rule_url in rules_url:
    print('loading... ' + rule_url)

    # get rule text
    success = False
    try_times = 0
    r = None
    while try_times < 5 and not success:
        r = requests.get(rule_url)
        if r.status_code != 200:
            time.sleep(1)
            try_times = try_times + 1
        else:
            success = True
            break

    if not success:
        sys.exit('error in request %s\n\treturn code: %d' % (rule_url, r.status_code))

    rule_text = rule_text + r.text + '\n'

# parse rule
rules = rule_text.split('\n')
for rule in rules:
    rule = rule.strip()
    row0 = rule

    # 处理广告例外规则

    if rule.startswith('@@'):
        i = 0
        while i < len(domains):
            domain = domains[i]
            if domain in rule:
                del domains[i]
            else:
                i = i + 1

        continue

    # 处理广告黑名单规则

    # 直接跳过
    if rule == '' or rule.startswith('!') or "$" in rule or "##" in rule:
        continue

    # 清除前缀
    rule = re.sub(r'^\|?https?://', '', rule)
    rule = re.sub(r'^\|\|', '', rule)
    rule = rule.lstrip('.*')

    # 清除后缀
    rule = rule.rstrip('/^*')
    rule = re.sub(r':\d{2,5}$', '', rule)  # 清除端口

    # 不能含有的字符
    if re.search(r'[/^:*]', rule):
        print('ignore: ' + row0)
        continue

    # 只匹配域名或 IP
    if re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,9}$', rule) or re.match(
            r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', rule):
        domains.append(rule)

print('done.')

# write into files

file_ad = sys.stdout
try:
    if sys.version_info.major == 3:
        file_ad = open('resultant/ad.list', 'w', encoding='utf-8')
    else:
        file_ad = open('resultant/ad.list', 'w')
except:
    pass

file_ad.write('# adblock rules refresh time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')

domains = list(set(domains))
domains.sort()

for item in domains:
    file_ad.write(item + '\n')
