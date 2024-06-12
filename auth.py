import hashlib
import hmac
import json
import os
import re
import requests
import time
import logging

from dotenv import load_dotenv

from utils import encrypt


logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)


# 参数初始化
def init_params():
    # 固定参数
    init_url = "http://172.16.1.11"
    url_get_challenge = init_url + "/cgi-bin/get_challenge"
    url_srun_portal = init_url + "/cgi-bin/srun_portal"
    ac_id = "1"
    n = "200"
    type = "1"
    enc = "srun_bx1"
    operate_system = "Windows 10"
    name = "Windows"
    time_stamp = int(time.time())
    callback = "jQuery112405642667473880212_" + str(time_stamp)

    headers = {
        'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, '
                  '*/*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'lang=zh-CN',
        'Dnt': '1',
        'Host': '172.16.1.11',
        'Pragma': 'no-cache',
        'Referer': 'http://172.16.1.11/srun_portal_pc?ac_id=1&theme=basic1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/113.0.0.0'
                      'Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    params = {
        'init_url': init_url,
        'url_get_challenge': url_get_challenge,
        'url_srun_portal': url_srun_portal,
        'headers': headers,
        'ac_id': ac_id,
        'n': n,
        'type': type,
        'enc': enc,
        'operate_system': operate_system,
        'name': name,
        'callback': callback,
    }

    logging.info("参数初始化完成")

    return params


# 获取内网 ip 地址
def get_local_ip(headers, init_url):
    try:
        home_page_url = init_url + "/srun_portal_pc?ac_id=1&theme=pro"
        init_res = requests.get(home_page_url, headers=headers)
        init_res.raise_for_status()
        pattern = r'ip\s+:\s+"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)"'
        match = re.search(pattern, init_res.text)
        ip_address = match.group(1)

        logging.info("获取当前要登录的内网 ip 完成：" + ip_address)

        return ip_address
    except requests.RequestException as e:
        logging.error("获取当前内网 ip 失败：" + e)
        exit()


# 使用 callback 获取 token
def get_token(headers, url_get_challenge, callback, username, ip):
    try:
        get_challenge_params = {
            'callback': callback,
            'username': username,
            'ip': ip,
            '_': str(int(time.time()))
        }

        response = requests.get(url_get_challenge, headers=headers, params=get_challenge_params)
        response.raise_for_status()
        return analysis_jsonp(response)['challenge']
    except requests.RequestException as e:
        logging.error("获取 token 失败：" + e)
        exit()


# 解析 jsonp
def analysis_jsonp(response):
    try:
        jsonp_response = response.text
        json_data = re.search(r'\(({.*})\)', jsonp_response).group(1)
        data = json.loads(json_data)
        logging.info("成功解析 jsonp 数据：" + json_data)
        return data
    except json.JSONDecodeError as e:
        logging.error("解析 jsonp 数据失败：" + e)
        exit()


# 判断 ip 地址（用于区分实验室网络与寝室网络）
def adjust_ip(ip_address):
    first_two_octets = ip_address.split(".")[0:2]
    result = ".".join(first_two_octets)

    username = os.environ.get('USERNAME_STUDENT_ID')
    password = os.environ.get('PASSWORD_STUDENT_ID')

    if not username or not password:
        logging.error('Environment variables USERNAME_STUDENT_ID and PASSWORD_STUDENT_ID are not set')
        exit()

    if result != "10.31":
        username = os.environ.get('USERNAME_PHONE')
        password = os.environ.get('PASSWORD_PHONE')

        if not username or not password:
            logging.error('Environment variables USERNAME_PHONE and PASSWORD_PHONE are not set')
            exit()

    logging.info("当前登录的用户：" + username)

    return username, password


# 对密码进行 hmac-md5 加密
def hmac_md5(message, key):
    hmac_hash = hmac.new(key.encode(), message.encode(), hashlib.md5)
    return hmac_hash.hexdigest()


# 对数据进行签名
def encrypt_sign(headers, url_get_challenge, username, password, ip, callback, ac_id, enc):
    token = get_token(headers, url_get_challenge, callback, username, ip)
    hmd5 = hmac_md5(password, token)
    logging.info("hmd5 : " + hmd5)
    info = {
        "username": username,
        "password": password,
        "ip": ip,
        "acid": ac_id,
        "enc_ver": enc
    }
    i = "{SRBX1}" + encrypt.new(json.dumps(info), token)
    logging.info("i : " + i)
    logging.info("成功加密数据")
    return i, hmd5, token


# 拼接字符串
def get_chkstr(token, username, hmd5, ac_id, ip, n, type, i):
    chkstr = token + username
    chkstr += token + hmd5
    chkstr += token + ac_id
    chkstr += token + ip
    chkstr += token + n
    chkstr += token + type
    chkstr += token + i
    return chkstr


# 登录
def login(headers, url_srun_portal, username, ip, ac_id, i, hmd5, chksum, n, type, operate_system, name, callback):
    try:
        srun_portal_params = {
            'callback': callback,
            'action': 'login',
            'username': username,
            'password': '{MD5}' + hmd5,
            'ac_id': ac_id,
            'ip': ip,
            'chksum': chksum,
            'info': i,
            'n': n,
            'type': type,
            'os': operate_system,
            'name': name,
            'double_stack': '1',
            '_': str(int(time.time()))
        }

        srun_portal_response = requests.get(url_srun_portal, headers=headers, params=srun_portal_params)
        srun_portal_response.raise_for_status()
        srun_portal_response_json = analysis_jsonp(srun_portal_response)

        if srun_portal_response_json["error"] == "ok":
            logging.info("登录成功")
        else:
            logging.error("登录失败")
            logging.error(srun_portal_response_json['error_msg'])
    except requests.RequestException as e:
        logging.error(e)
        exit()


def run():
    # load environments
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

    # init params
    params = init_params()

    # get ip
    ip = get_local_ip(params['headers'], params['init_url'])

    username, password = adjust_ip(ip)

    # utils params
    i, hmd5, token = encrypt_sign(params['headers'], params['url_get_challenge'], username, password, ip,
                                  params['callback'], params['ac_id'], params['enc'])
    chkstr = get_chkstr(token, username, hmd5, params['ac_id'], ip, params['n'], params['type'], i)
    chksum = hashlib.sha1(chkstr.encode()).hexdigest()

    # login
    login(params['headers'], params['url_srun_portal'], username, ip, params['ac_id'], i, hmd5, chksum, params['n'],
          params['type'], params['operate_system'], params['name'], params['callback'])


if __name__ == '__main__':
    run()
