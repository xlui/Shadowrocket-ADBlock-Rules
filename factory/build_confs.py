# -*- coding: utf-8 -*-

import re
import time


def getRulesStringFromFile(path, kind):
    file = open(path, 'r', encoding='utf-8')
    contents = file.readlines()
    ret = ''

    for content in contents:
        content = content.strip('\r\n')
        if not len(content):
            continue

        if content.startswith('#'):
            ret += content + '\n'
        else:
            prefix = 'DOMAIN-SUFFIX'
            if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content):
                prefix = 'IP-CIDR'
                if '/' not in content:
                    content += '/32'
            elif '.' not in content:
                prefix = 'DOMAIN-KEYWORD'

            ret += prefix + ',%s,%s\n' % (content, kind)

    return ret


# get head and foot
str_head = open('template/sr_head.txt', 'r', encoding='utf-8').read()
str_foot = open('template/sr_foot.txt', 'r', encoding='utf-8').read()

# mask values
values = {}

values['build_time'] = time.strftime("%Y-%m-%d %H:%M:%S")

# REJECT
values['ad'] = getRulesStringFromFile('resultant/ad.list', 'Reject')
values['manual_reject'] = getRulesStringFromFile('manual/reject.txt', 'Reject')

# DIRECT
values['top500_direct'] = getRulesStringFromFile('resultant/top500_direct.list', 'Direct')
values['manual_direct'] = getRulesStringFromFile('manual/direct.txt', 'Direct')

# PROXY
values['manual_proxy'] = getRulesStringFromFile('manual/proxy.txt', 'Proxy')
values['top500_proxy'] = getRulesStringFromFile('resultant/top500_proxy.list', 'Proxy')

# generate conf
conf_name = 'sr_top500_whitelist_ad'
template = open(f'template/{conf_name}.txt', 'r', encoding='utf-8').read()
template = str_head + template + str_foot
file_output = open('../' + conf_name + '.conf', 'w', encoding='utf-8')

marks = re.findall(r'{{(.+)}}', template)
for mark in marks:
    template = template.replace('{{' + mark + '}}', values[mark])

file_output.write(template)
