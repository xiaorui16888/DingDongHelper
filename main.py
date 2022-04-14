# -*- coding: UTF-8 -*-
"""
@Project ：DingDongHelper
@File    ：main.py
@IDE     ：PyCharm 
@Author  ：胖妞
@Date    ：2022/4/13 10:01
"""
import logging
import warnings
from ruamel import yaml
import time

import requests

# 初始化日志以及警告配置
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
                    datefmt='%Y-%m-%d %A %H:%M:%S')
warnings.filterwarnings('ignore')

GETUserAddressUrl = 'https://sunquan.api.ddxq.mobi/api/v1/user/address/'
GETCardProductUrl = 'https://maicai.api.ddxq.mobi/cart/index'
GetMultiReserveTimeUrl = 'https://maicai.api.ddxq.mobi/order/getMultiReserveTime'

user_content = open('./user.yml', 'r', encoding='utf-8')
user_config = yaml.load(user_content.read(), Loader=yaml.Loader)

common_header = {
    'Host': 'maicai.api.ddxq.mobi',
    'Connection': 'keep-alive',
    'Content-Length': '6941',
    'Cookie': user_config['Cookie'],
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
    'content-type': 'application/x-www-form-urlencoded',
    'ddmc-api-version': '9.49.2',
    'ddmc-app-client-id': '4',
    'ddmc-build-version': '2.82.0',
    'ddmc-channel': 'applet',
    'ddmc-city-number': user_config['city_number'],
    'ddmc-device-id': user_config['device_id'],
    'ddmc-ip': '',
    'ddmc-latitude': user_config['latitude'],
    'ddmc-longitude': user_config['longitude'],
    'ddmc-os-version': '[object Undefined]',
    'ddmc-station-id': user_config['station_id'],
    'ddmc-uid': user_config['uid'],
    'Referer': 'https://servicewechat.com/wx1e113254eda17715/422/page-frame.html',
    'Accept-Encoding': 'gzip, deflate, br',
}

common_params = {
    'uid': user_config['uid'],
    'longitude': user_config['longitude'],
    'latitude': user_config['latitude'],
    'station_id': user_config['station_id'],
    'city_number': user_config['city_number'],
    'api_version': '9.49.2',
    'app_version': '2.82.0',
    'applet_source': '',
    'channel': 'applet',
    'app_client_id': '4',
    'sharer_uid': '',
    'openid': user_config['openid'],
    'h5_source': '',
    'device_token': user_config['device_token'],
    'is_load': '1',
}


# 获取收货地址--address_id,station_id
def getValidAddress():
    if user_config['Cookie'] == '':
        logging.error("------------------- cookie配置错误，请配置 ------------------- ")
        exit()

    header = {
        'Host': 'sunquan.api.ddxq.mobi',
        'Connection': 'keep-alive',
        'Cookie': user_config['Cookie'],
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
        'content-type': 'application/x-www-form-urlencoded',
        'Referer': 'https://servicewechat.com/wx1e113254eda17715/422/page-frame.html',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    response = requests.get(url=GETUserAddressUrl, timeout=10000, headers=header, verify=False).json()
    if not response['success']:
        logging.error(response['message'])
        exit()

    addressList = response['data']['valid_address']
    if len(addressList) == 0:
        logging.info("！！！你怎么不设置收货地址呢！！！")
        exit()

    logging.info("------------------- 获取到{0}个地址 ------------------- ".format(len(addressList)))
    for index, address in enumerate(addressList):
        logging.info(
            "\n######地址{0}######\n姓名：{1}\n手机号：{2}\n收货人地址：{3}\n小区名称：{4}\n详细地址：{5}\nstation_id：{6}\naddress_id：{7}\n".
                format(index + 1, address['user_name'], address['mobile'], address['location']['address'],
                       address['location']['name'], address['addr_detail'], address['station_id'], address['id']))


# 获取购物车商品信息
def getCardMsg():
    common_header['is_load'] = '1'
    response = requests.post(url=GETCardProductUrl, timeout=10000, headers=common_header, data=common_params,
                             verify=False).json()
    print(response)
    try:
        products = '[{0}]'.format(str(response['data']['product']['effective'][0]['products']))
        print(products)
        with open('./card.yml', "w", encoding="utf-8") as f:
            yaml.dump({'products': products}, f, Dumper=yaml.RoundTripDumper)
    except:
        logging.error("！购物车商品都失效了，你先随便添加个商品到你的购物车吧！")
        exit()


# 监控运力
def getMultiReserveTime():
    card_content = open('./card.yml', 'r', encoding='utf-8')
    card_config = yaml.load(card_content.read(), Loader=yaml.Loader)
    if card_config['products'] == '':
        logging.error("！购物车商品都失效了，你先随便添加个商品到你的购物车吧！")
        exit()

    resp = requests.get('{0}?do=remote&msg=你已经开启微信通知模式&to_wxid={1}'.format(user_config['notice_url'],
                                                                           user_config['to_wxid']))
    if resp.status_code == requests.codes.ok:
        logging.info("------------------- 通知开启成功 ------------------- ")
    else:
        logging.error("------------------- 通知开启失败 ------------------- ")
        exit()

    common_params['products'] = card_config['products'].replace('False', 'false')
    common_params['isBridge'] = 'false'
    common_params['group_config_id'] = ''
    common_params['address_id'] = user_config['address_id']
    while True:
        response = requests.post(url=GetMultiReserveTimeUrl, timeout=10000, headers=common_header, data=common_params,
                                 verify=False).json()

        try:
            day_times = response['data'][0]['time'][0]['times']
            can_order = False

            for t in day_times:
                if t['disableType'] == 0 and t['select_msg'] != '自动尝试可用时段':
                    can_order = True
                    break
            if can_order:
                select_msg = str(response['data'][0]['time'][0]['select_msg'])
                logging.info(
                    "----- 今天可以选择付款时间段！！请火速抢购 -----" + select_msg)
                resp = requests.get('{0}?do=remote&msg=今天可以选择付款时间段！！请火速抢购&to_wxid={1}'.format(user_config['notice_url'],
                                                                                              user_config['to_wxid']))
                if resp.status_code == requests.codes.ok:
                    logging.info("------------------- 通知发送成功 ------------------- ")
                else:
                    logging.error("------------------- 通知发送失败 ------------------- ")
            else:
                logging.info(
                    "------------------- 今天暂无可以订购的时段！ --------------" + str(response['data'][0]['time'][0]['times']))

            time.sleep(user_config['sleep_time'])
        except:
            logging.error('~~~兄弟，你的账号怕是掉线了~~~')
            exit()


if __name__ == '__main__':
    print('本项目纯属学习使用，不可用作商业行为！任何违法违规造成的问题与本人无关！')
    # 第一步，需要你抓包后，手动配置user.yml里面的参数，

    # # 获取收货地址--address_id，station_id。获取到后需要手动配置到user.yml里面
    getValidAddress()
    # # 获取购物车内商品信息，写入到card.yml，用于监控运力。
    getCardMsg()
    # # 监控运力进行通知，可以一直挂在服务器上或者本地，用于捡漏
    getMultiReserveTime()
