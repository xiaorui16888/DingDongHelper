# -*- coding: UTF-8 -*-
"""
@Project ：DingDongHelper 
@File    ：main.py
@IDE     ：PyCharm 
@Author  ：胖妞
@Date    ：2022/4/24 1:58
"""

import requests
from ruamel import yaml
import time
import logging
from logging import handlers
from wxpusher import WxPusher
import sys
import execjs
import json
import hashlib
import random
import threading


# 初始化日志以及警告配置
class Logger(object):
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }  # 日志级别关系映射

    def __init__(self, filename, level='info', when='D', backCount=3,
                 fmt='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)  # 设置日志格式
        self.logger.setLevel(self.level_relations.get(level))  # 设置日志级别
        sh = logging.StreamHandler()  # 往屏幕上输出
        sh.setFormatter(format_str)  # 设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')  # 往文件里写入#指定间隔时间自动生成文件的处理器
        th.setFormatter(format_str)  # 设置文件里写入的格式
        self.logger.addHandler(sh)  # 把对象加到logger里
        self.logger.addHandler(th)


log = Logger('all.log', level='debug')

user_content = open('user.yaml', 'r', encoding='utf-8')
user_config = yaml.load(user_content.read(), Loader=yaml.Loader)


def getCartData():
    GET_CART_API = f"https://maicai.api.ddxq.mobi/cart/index?" \
                   f"?ab_config=%7B%22key_onion%22:%22D%22,%22key_cart_discount_price%22:%22C%22%7D" \
                   f"&api_version={user_config['api_version']}" \
                   f"&app_client_id={user_config['app_client_id']}" \
                   f"&app_version={user_config['build_version']}" \
                   f"&applet_source=" \
                   f"&channel=applet" \
                   f"&city_number={user_config['city_number']}" \
                   f"&h5_source=" \
                   f"&is_load=1" \
                   f"&latitude={user_config['latitude']}" \
                   f"&longitude={user_config['longitude']}" \
                   f"&share_uid=" \
                   f"&station_id={user_config['station_id']}" \
                   f"&time={int(time.time())}" \
                   f"&openid=2088822731166895" \
                   f"&uid={user_config['uid']}"

    payload = {}
    response = requests.request("GET", GET_CART_API, headers=COMMON_HEADERS, data=payload).json()
    # log.logger.info('购物车接口响应' + str(response))
    print('获取购物车---', response)
    if response['code'] == 0:
        print('获取购物车===更新购物车数据成功')
        # if len(response['data']['product']['invalid'][0]) == 0:
        if len(response['data']['new_order_product_list']) == 0:
            print('获取购物车===购物车无可买的商品')
            return
        new_order_product_list = response['data']['new_order_product_list'][0]
        # new_order_product_list = response['data']['product']['invalid'][0]
        products = new_order_product_list['products']
        # print(products)

        for product in products:
            product['total_money'] = product['total_price']
            product['total_origin_money'] = product['total_origin_price']
        print("获取购物车===订单总金额：" + response['data']['total_money'])

        data = {
            'products': products,
            'parent_order_sign': response['data']['parent_order_info']['parent_order_sign'],
            'total_money': response['data']['total_money'],
            'total_origin_money': response['data']['new_order_product_list'][0]['total_origin_money'],
            'goods_real_money': response['data']['goods_real_money'],
            'total_count': response['data']['total_count'],
            'cart_count': response['data']['cart_count'],
            'is_presale': new_order_product_list['is_presale'],
            'instant_rebate_money': response['data']['instant_rebate_money'],
            'used_balance_money': new_order_product_list['used_balance_money'],
            'can_used_balance_money': new_order_product_list['can_used_balance_money'],
            'used_point_num': new_order_product_list['used_point_num'],
            'used_point_money': new_order_product_list['used_point_money'],
            'is_share_station': new_order_product_list['is_share_station'],
            'only_today_products': new_order_product_list['only_today_products'],
            'only_tomorrow_products': new_order_product_list['only_tomorrow_products'],
            'package_type': new_order_product_list['package_type'],
            'package_id': new_order_product_list['package_id'],
            'front_package_text': new_order_product_list['front_package_text'],
            'front_package_type': new_order_product_list['front_package_type'],
            'front_package_stock_color': new_order_product_list['front_package_stock_color'],
            'front_package_bg_color': new_order_product_list['front_package_bg_color'],
        }

        return data
    elif response['code'] == '405':
        print('获取购物车===' + '接口访问频繁')
        time.sleep(5)  # 接口访问频繁的情况下，先暂停5秒
    elif response['code'] == -3000:
        print('获取购物车===' + response['msg'])
        time.sleep(5)  # 接口访问频繁的情况下，先暂停5秒
    elif '已过期' in response['msg']:
        print('获取购物车===' + response['msg'])
        return 0


def getMultiReserveTime(products):
    if len(products) == 0:
        return
    GetMultiReserveTime_API = "https://maicai.api.ddxq.mobi/order/getMultiReserveTime"

    payload = {
        'uid': user_config['uid'],
        'longitude': user_config['longitude'],
        'latitude': user_config['latitude'],
        'station_id': user_config['station_id'],
        'city_number': user_config['city_number'],
        'api_version': user_config['api_version'],
        'app_version': user_config['build_version'],
        'applet_source': '',
        'app_client_id': user_config['app_client_id'],
        'h5_source': '',
        'wx': '1',
        'sharer_uid': '',
        'openid': '',
        'time': int(time.time()),
        'address_id': user_config['address_id'],
        'group_config_id': '',
        'products': '[' + str(products) + ']',
        'isBridge': 'false'
    }

    text = execjs.compile(open(r'sign.js').read())
    # body签名
    signData = json.loads(text.call('sign', json.dumps(payload, ensure_ascii=False)))
    payload['nars'] = signData['nars']
    payload['sesi'] = signData['sesi']
    response = requests.request("POST", GetMultiReserveTime_API, headers=COMMON_HEADERS, data=payload).json()
    # log.logger.info('运力接口响应数据'+str(response))

    try:
        times = response['data'][0]['time'][0]['times']
        for time_item in times:
            if int(time_item['disableType']) == 0 and time_item['select_msg'].find('尽快') < 0:
                print('更新配送时间成功')
                return {'reserved_time_start': time_item['start_timestamp'],
                        'reserved_time_end': time_item['end_timestamp']}
    except:
        print('获取运力===' + response['msg'])


def checkOrder():
    if reserve_data is None:
        return
    cart_products['reserved_time'] = {"reserved_time_start": reserve_data['reserved_time_start'],
                                      "reserved_time_end": reserve_data['reserved_time_end'], "time_biz_type": 0}

    url = "https://maicai.api.ddxq.mobi/order/checkOrder"

    payload = {
        'uid': user_config['uid'],
        'longitude': user_config['longitude'],
        'latitude': user_config['latitude'],
        'station_id': user_config['station_id'],
        'city_number': user_config['city_number'],
        'api_version': user_config['api_version'],
        'app_version': user_config['build_version'],
        'applet_source': '',
        'app_client_id': user_config['app_client_id'],
        'h5_source': '',
        'wx': '1',
        'sharer_uid': '',
        'openid': '',
        'time': int(time.time()),
        'address_id': user_config['address_id'],
        'user_ticket_id': 'default',
        'freight_ticket_id': 'default',
        'is_use_point': '0',
        'is_use_balance': '0',
        'is_buy_vip': '0',
        'coupons_id': '',
        'is_buy_coupons': 0,
        'packages': '[' + str(cart_products) + ']',
        'check_order_type': '0',
        'is_support_merge_payment': '1',
        'showData': 'true',
        'showMsg': 'false',
    }

    text = execjs.compile(open(r'sign.js').read())
    # body签名
    signData = json.loads(text.call('sign', json.dumps(payload, ensure_ascii=False)))
    payload['nars'] = signData['nars']
    payload['sesi'] = signData['sesi']

    response = requests.request("POST", url, headers=COMMON_HEADERS, data=payload).json()
    print('校验订单===', response)
    # exit()
    if response['success'] != 'false' and response['code'] == 0:
        cart_products['freight_discount_money'] = response['data']['order']['freight_discount_money']
        cart_products['freight_money'] = response['data']['order']['freight_money']
        cart_products['total_money'] = response['data']['order']['total_money']
        cart_products['freight_real_money'] = response['data']['order']['freight_real_money']
        return cart_products


def addNewOrder():
    if packages_data is None:
        return
    url = "https://maicai.api.ddxq.mobi/order/addNewOrder"
    # print('packages_data', packages_data)
    packages_data['reserved_time_start'] = packages_data['reserved_time']['reserved_time_start']
    packages_data['reserved_time_end'] = packages_data['reserved_time']['reserved_time_end']
    package_order = {
        "payment_order": {
            "reserved_time_start": reserve_data['reserved_time_start'],
            "reserved_time_end": reserve_data['reserved_time_end'],
            "price": packages_data['total_money'],
            "freight_discount_money": packages_data['freight_discount_money'],
            "freight_money": packages_data['freight_money'],
            "order_freight": packages_data['freight_real_money'],
            "parent_order_sign": packages_data['parent_order_sign'],
            "product_type": 1,
            "address_id": user_config['address_id'],
            "receipt_without_sku": 0,
            "pay_type": user_config['pay_type'],
            "vip_money": "",
            "vip_buy_user_ticket_id": "",
            "coupons_money": "",
            "coupons_id": ""
        },
        'packages': packages_data
    }
    # print('package_order', package_order)
    payload = {
        'uid': user_config['uid'],
        'longitude': user_config['longitude'],
        'latitude': user_config['latitude'],
        'station_id': user_config['station_id'],
        'city_number': user_config['city_number'],
        'api_version': user_config['api_version'],
        'app_version': user_config['build_version'],
        'applet_source': '',
        'app_client_id': user_config['app_client_id'],
        'h5_source': '',
        'sharer_uid': '',
        'openid': '',
        'time': int(time.time()),
        'package_order': '' + str(package_order) + '',
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

    response = requests.request("POST", url, headers=COMMON_HEADERS, data=payload).json()
    log.logger.info('下单接口响应数据' + str(response))
    # print('下单数据', response)
    if response['success'] != 'false' and response['code'] == 0:
        WxPusher.send_message('抢菜成功！！快去支付',
                              uids=[user_config['wxpush_id']],
                              topic_ids=[],
                              token='AT_8Irjy2ThxbL0ydz0Q9R0geWl2X1nkHea')
        log.logger.info('抢菜成功！！快去支付')
        return True
    else:
        log.logger.info('---未成功---')


def allCheck():
    GET_CART_API = f"https://maicai.api.ddxq.mobi/cart/allCheck?" \
                   f"ab_config=%7B%22key_onion%22:%22D%22,%22key_cart_discount_price%22:%22C%22%7D" \
                   f"&api_version={user_config['api_version']}" \
                   f"&app_client_id={user_config['app_client_id']}" \
                   f"&app_version={user_config['build_version']}" \
                   f"&applet_source=" \
                   f"&applet_source=applet" \
                   f"&city_number={user_config['city_number']}" \
                   f"&h5_source=" \
                   f"&is_check=1" \
                   f"&is_load=1" \
                   f"&latitude={user_config['latitude']}" \
                   f"&longitude={user_config['longitude']}" \
                   f"&openid=" \
                   f"&sharer_uid=" \
                   f"&station_id={user_config['station_id']}" \
                   f"&time={int(time.time())}" \
                   f"&uid={user_config['uid']}"

    payload = {}
    response = requests.request("GET", GET_CART_API, headers=COMMON_HEADERS, data=payload).json()
    # print(response)
    if response['code'] == 0 and response['success'] != 'false':
        print('商品全选成功')


def getOneAddress():
    header = {
        'Host': 'sunquan.api.ddxq.mobi',
        'Connection': 'keep-alive',
        'Cookie': user_config['cookie'],
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
        'content-type': 'application/x-www-form-urlencoded',
        'Referer': 'https://servicewechat.com/wx1e113254eda17715/422/page-frame.html',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    response = requests.request('get', url='https://sunquan.api.ddxq.mobi/api/v1/user/address/?'
                                           'app_client_id='+str(user_config['app_client_id'])+'&h5_source=&wx=1&sharer_uid=', timeout=10000,
                                headers=header,
                                ).json()
    print(response)
    addressList = response['data']['valid_address']
    print("------------------- 获取到{0}个地址 ------------------- ".format(len(addressList)))
    address = addressList[0]
    user_config['station_id'] = address['station_id']
    user_config['address_id'] = address['id']
    user_config['longitude'] = str(address['location']['location'][0])
    user_config['latitude'] = str(address['location']['location'][1])
    user_config['city_number'] = str(address['city_number'])


# 获取默认地址，这里你最好只留一个地址...
getOneAddress()

COMMON_HEADERS = {
    'ddmc-os-version': 'undefined',
    'Origin': 'https://wx.m.ddxq.mobi',
    'Host': 'maicai.api.ddxq.mobi',
    'Cookie': user_config['cookie'],
    'User-Agent': user_config['user_agent'],
    'ddmc-city-number': user_config['city_number'],
    'ddmc-api-version': user_config['api_version'],
    'ddmc-build-version': user_config['build_version'],
    'ddmc-longitude': user_config['longitude'],
    'ddmc-latitude': user_config['latitude'],
    'ddmc-app-client-id': user_config['app_client_id'],
    'Connection': 'keep-alive',
    'ddmc-uid': user_config['uid'],
    'ddmc-device-id': '',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'ddmc-channel': 'undefined',
    'Accept-Charset': 'UTF-8',
    'ddmc-ip': '',
    'ddmc-time': str(int(time.time())),
    'content-Type': 'application/x-www-form-urlencoded',
    'ddmc-station-id': user_config['station_id'],
    'Referer': 'https://wx.m.ddxq.mobi/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'ddmc-sdkversion': '0',
    'x-release-type': 'ONLINE',
}

if __name__ == '__main__':
    word = user_config['uid'] + user_config['uid'][::-1]
    if hashlib.md5(word.encode(encoding='UTF-8')).hexdigest() != user_config['activate_key']:
        input('秘钥错误')
        # 校验拥挤情况：获取运力、获取商品接口拥挤--待完善
    while True:
        try:
            allCheck()  # 勾选全部商品
            cart_products = getCartData()  # 获取购物车
            if cart_products:  # 如果获取到购物车有效商品
                reserve_data = getMultiReserveTime(cart_products['products'])  # 查询可配送时间
                if reserve_data is not None:  # 如果有运力的情况下，再执行下方操作
                    for check_index in range(5):  # 一般抢菜都会遇到拥挤情况，所以这里我提交5次
                        packages_data = checkOrder()  # 校验订单
                        if packages_data:
                            print('提交校验---{0}---次'.format(check_index + 1))

                            add_order_replay_num = 5
                            if user_config['buy_model'] == 1:
                                add_order_replay_num = 5
                            else:
                                add_order_replay_num = 10

                            for add_index in range(add_order_replay_num):  # 一般抢菜都会遇到拥挤情况，所以这里我提交5次支付
                                print('提交支付---{0}---次'.format(add_index + 1))
                                if addNewOrder():  # 抢菜成功了，终止循环
                                    input('！！！抢购成功！！！')
                                    sys.exit()

                else:
                    print('获取运力===暂无可配送时间')

            elif cart_products == 0:  # 检测到账号掉线，先终止程序。本来这里用的sys.exit()，但是打包成exe后，如此写法会直接关闭掉cmd窗口，我查了资料，也没找到合适的方法，赶时间只能写这样了
                WxPusher.send_message('你已掉线~请重新配置账号信息',
                                      uids=[user_config['wxpush_id']],
                                      topic_ids=[],
                                      token='AT_8Irjy2ThxbL0ydz0Q9R0geWl2X1nkHea')
                input('你已掉线~请重新配置账号信息')

            if user_config['buy_model'] == 1:  # 哨兵模式
                # 下一次捡漏时间
                random_sleep_time = random.randint(user_config['sleep_time_left'], user_config['sleep_time_right'])
                print('---{0}秒后继续捡漏---'.format(random_sleep_time))
                time.sleep(random_sleep_time)
            else:  # 暴利模式
                time.sleep(user_config['sleep_time_spike'])
        except Exception as e:
            log.logger.error('啊~程序出错了！===', e)
            print('---{0}--秒后继续捡漏'.format(user_config['sleep_error_time']))
            time.sleep(user_config['sleep_error_time'])
            pass
