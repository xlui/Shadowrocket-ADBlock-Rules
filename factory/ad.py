# -*- coding: utf-8 -*-

#
# 1. 提取广告规则，并且只提取对全域禁止的那种规则
# 2. 从 hosts 提取屏蔽域名
#

import re
import sys
import time

# 域名白名单
import requests

domain_whitelist = {
    'localhost',
    'localhost.localdomain',
    'local',
    'broadcasthost',
    'ip6-localhost',
    'ip6-loopback',
    'ip6-localnet',
    'ip6-mcastprefix',
    'ip6-allnodes',
    'ip6-allrouters',
    'ip6-allhosts',
    '0.0.0.0',
}
# AdBlock rule list
rule_urls = [
    # EasyList China
    # 'https://easylist-downloads.adblockplus.org/easylistchina.txt',
    # EasyList + China
    'https://easylist-downloads.adblockplus.org/easylistchina+easylist.txt',
    # 乘风 广告过滤规则
    'https://raw.githubusercontent.com/xinggsf/Adblock-Plus-Rule/master/ABP-FX.txt'
]
# Ad hosts list
hosts_urls = [
    'https://raw.githubusercontent.com/VeleSila/yhosts/master/hosts.txt',
    'https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts',
    'https://raw.githubusercontent.com/jdlingyu/ad-wars/master/hosts',
    'https://raw.githubusercontent.com/Goooler/1024_hosts/master/hosts',
]


def load_url(url):
    success = False
    try_times = 0
    r = None
    while try_times < 5 and not success:
        r = requests.get(url)
        if r.status_code != 200:
            time.sleep(1)
            try_times = try_times + 1
        else:
            success = True
            break

    if not success:
        sys.exit('error in request %s\n\treturn code: %d' % (rule_url, r.status_code))
    return r.text


# Parse AdBlock rules, extracts ad domain or IP.
def parse_rules():
    print('[rule parse] start...')
    _res = []
    # Fetch rule text
    rule_text = ''
    for rule_url in rule_urls:
        rule_text += load_url(rule_url) + '\n'
    # Parse rule
    rules = rule_text.split('\n')
    for rule in rules:
        rule = rule.strip()
        row0 = rule

        # 处理广告例外规则
        if rule.startswith('@@'):
            i = 0
            while i < len(_res):
                domain = _res[i]
                if domain in rule:
                    del _res[i]
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
            print('[rule parse] ignore: ' + row0)
            continue

        # 只匹配域名或 IP
        if re.match(r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,9}$', rule) or re.match(
                r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', rule):
            _res.append(rule)

    print('[rule parse] done.')
    return _res


# Hosts - Parse Anti-AD hosts, extract domains.
def parse_hosts():
    print('[host parse] start...')
    _res = []
    # Fetch hosts text
    hosts_text = ''
    for hosts_url in hosts_urls:
        hosts_text += load_url(hosts_url)
    # Parse hosts
    hosts = hosts_text.split('\n')
    for host in hosts:
        if '#' in host:
            host = host[:host.index('#')]
        host = host.strip()
        # 移除注释
        if not host or \
                host.startswith('#') or \
                host.startswith('@') or \
                host.startswith('::1'):
            print(f'[host parse] ignore: {host}')
            continue

        # 解析行内容
        words = host.split(' ')
        if len(words) < 2:
            print(f'[host parse] invalid hosts format:\nhost:{host}, words:{words}')
            continue

        domain = words[-1]
        if domain in domain_whitelist:
            continue
        _res.append(domain)
    print('[host parse] done.')
    return _res


# Save ad domain names into file
def save(_domains):
    file_ad = sys.stdout
    try:
        if sys.version_info.major == 3:
            file_ad = open('resultant/ad.list', 'w', encoding='utf-8')
        else:
            file_ad = open('resultant/ad.list', 'w')
    except:
        pass

    file_ad.write('# adblock rules refresh time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')

    _domains = list(set(_domains))
    _domains.sort()

    for item in _domains:
        file_ad.write(item + '\n')


save(parse_rules() + parse_hosts())
