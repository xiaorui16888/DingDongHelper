# -*- coding: UTF-8 -*-
"""
@Project ：DingDongHelper 
@File    ：test.py
@IDE     ：PyCharm 
@Author  ：胖妞
@Date    ：2022/4/25 9:26
"""

# python文件
import execjs
import json


payload = {
    'showData': 'true',
    'showMsg': 'false',
    'ab_config': '{"key_onion":"C"}',
    'channel': 'applet'
}

text = execjs.compile(open(r'sign.js').read())
# body签名
signData = json.loads(text.call('sign', json.dumps(payload, ensure_ascii=False)))
payload['nars'] = signData['nars']
payload['sesi'] = signData['sesi']

print(signData)