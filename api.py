from turtle import update
from flask import Flask, request
import requests
import json
from requests import HTTPError
import socket

app = Flask(__name__)

phone: str
password: str
token: str
account: dict
headers: dict

@app.route("/")
def index():
    return "Welcome!!"

@app.route("/api/login/", methods=['POST'])
def login():
    global phone
    global password
    global token
    global headers

    url = 'https://b984b31f959b88f0.ol668.vip/user-client/auth/phone/login'
    payload = {}
    print(f"login: {request.json}")
    if request.json and "mobile" in request.json and "password" in request.json:
        payload = request.json
        phone = request.json['mobile']
        password = request.json['password']
    else:
        payload = {
            'mobile':phone,
            'password':password
        }

    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        
        re = json.loads(r.text)
        token = re['data']['token']

        headers = {
            'Authorization': 'Bearer ' + token,
            'Token': token,
            'Content-Type': 'application/json'
        }

        return info()

    except HTTPError as ex:
        return ex

@app.route("/api/info/", methods=['POST'])
def info(recall: bool = False):
    global account
    global headers

    url = 'https://b984b31f959b88f0.ol668.vip/user-client/user/get/info'

    print(f"Header: {headers}")

    try:
        r = requests.post(url, json={}, headers=headers)

        if r.status_code == 401 and recall == False:
            login()
            return info(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        account = re['data']
        account['ip_address'] = socket.gethostbyname(socket.gethostname())
        print(f"Account: {account}")
        return account

    except HTTPError as ex:
        return ex

@app.route("/api/competition/", methods=['GET'])
def competition(recall: bool = False):
    global headers
    url = 'https://b984b31f959b88f0.ol668.vip/base-client/competition/competition/hot'
    uid = account['uid']
    params = {
        'tz':'Asia/Phnom_Penh',
        'lang':'en',
        'uid':uid
    }

    try:
        r = requests.get(url, params=params, headers=headers)

        if r.status_code == 401 and recall == False:
            login()
            return competition(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re['data']

    except HTTPError as ex:
        return ex

@app.route("/api/competition/info", methods=['GET'])
def competition_info(recall: bool = False):
    global headers
    url = 'https://b984b31f959b88f0.ol668.vip/base-client/competition/competition/info'
    uid = account['uid']
    params = {
        'lang':'en',
        'uid':uid,
        'cid':request.args.get('cid')
    }

    print(f"Header: {headers}")

    try:
        r = requests.get(url, params=params, headers=headers)

        if r.status_code == 401 and recall == False:
            login()
            return competition_info(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re['data']

    except HTTPError as ex:
        return ex

@app.route("/api/competition/order", methods=['POST'])
def competition_order(recall: bool = False):
    global headers
    url = 'https://b984b31f959b88f0.ol668.vip/order-client/order/order'
    uid = account['uid']
    payload = {
        "lang":"en",
        "uid":uid,
        "cid":request.json['cid'],
        "amount": request.json['amount'],
        "odds": request.json['odds']
    }

    print(f"Header: {headers}")
    print(f"payload: {request.json}")

    try:
        r = requests.post(url, json=payload, headers=headers)
        
        if r.status_code == 401 and recall == False:
            login()
            return competition_order(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re

    except HTTPError as ex:
        return ex

@app.route("/api/order/record", methods=['POST'])
def order_record(recall: bool = False):
    global headers
    url = 'https://b984b31f959b88f0.ol668.vip/order-client/order/record'
    uid = account['uid']
    payload = {
        "lang":"en",
        "uid":uid,
        "type": 1,
        "page": 1,
        "startTime": request.json['startTime'],
        "endTime": request.json['endTime']
    }

    try:
        r = requests.post(url, json=payload, headers=headers)
        
        if r.status_code == 401 and recall == False:
            login()
            return order_record(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re

    except HTTPError as ex:
        return ex

# app.run()