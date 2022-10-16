from flask import Flask, request
import requests
import json
from requests import HTTPError
import socket
from flask_caching import Cache

config = {
    # "DEBUG": True,          # some Flask specific configs
    # "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DIR": "cache", # path to your server cache folder
    "CACHE_THRESHOLD": 100000, # number of 'files' before start auto-delete
    "CACHE_DEFAULT_TIMEOUT": 2592000
}

app = Flask(__name__)
app.config.from_mapping(config)

cache = Cache(app)
cache.set("url", "https://1e8f3e62cb143785.ol668.online")

@app.route("/")
def index():
    return "Welcome!!"

def getUrl(path: str) -> str:
    url = cache.get("url")
    return f"{url}{path}"

@app.route("/api/login/", methods=['POST'])
def login():
    url = getUrl('/user-client/auth/phone/login')
    payload = {}
    print(f"login: {request.json}")
    if request.json and "mobile" in request.json and "password" in request.json:
        payload = request.json
        phone = request.json['mobile']
        password = request.json['password']
        cache.set("phone", phone)
        cache.set("pass", password)
    else:
        payload = {
            'mobile':cache.get("phone"),
            'password':cache.get("pass")
        }

    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        
        re = json.loads(r.text)
        token = re['data']['token']
        cache.set("token", token)

        headers = {
            'Authorization': 'Bearer ' + token,
            'Token': token,
            'Content-Type': 'application/json'
        }
        cache.set("headers", headers)

        return re['data']

    except HTTPError as ex:
        return ex

@app.route("/api/info/", methods=['POST'])
def info(recall: bool = False):
    account = cache.get("account")
    headers = cache.get("headers")

    url = getUrl('/user-client/user/get/info')

    print(f"Header: {headers}")

    try:
        r = requests.post(url, json={}, headers=headers)

        if r.status_code == 401 and recall == False:
            return login()

        r.raise_for_status()
        
        re = json.loads(r.text)

        account = re['data']
        account['ip_address'] = socket.gethostbyname(socket.gethostname())
        cache.set("account", account)
        print(f"Account: {account}")
        return account

    except HTTPError as ex:
        return ex

@app.route("/api/competition/", methods=['GET'])
def competition(recall: bool = False):
    account = cache.get("account")
    headers = cache.get("headers")
    url = getUrl('/base-client/competition/competition/hot')
    uid = account['uid']
    params = {
        'tz':'Asia/Phnom_Penh',
        'lang':'en',
        'uid':uid
    }

    try:
        r = requests.get(url, params=params, headers=headers)

        if r.status_code == 401 and recall == False:
            login(True)
            return competition(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re['data']

    except HTTPError as ex:
        return ex

@app.route("/api/competition/info", methods=['GET'])
def competition_info(recall: bool = False):
    account = cache.get("account")
    headers = cache.get("headers")
    url = getUrl('/base-client/competition/competition/info')
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
            login(True)
            return competition_info(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re['data']

    except HTTPError as ex:
        return ex

@app.route("/api/competition/order", methods=['POST'])
def competition_order(recall: bool = False):
    headers = cache.get("headers")
    account = cache.get("account")
    url = getUrl('/order-client/order/order')
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
            login(True)
            return competition_order(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re

    except HTTPError as ex:
        return ex

@app.route("/api/url", methods=['PUT'])
def set_url():
    newUrl = request.json['url']
    cache.set("url", newUrl)

    response = '{"status": "ok", "code": 200, "msg": "update successfully"}'

    return json.loads(response)


@app.route("/api/order/record", methods=['POST'])
def order_record(recall: bool = False):
    headers = cache.get("headers")
    account = cache.get("account")
    url = getUrl('/order-client/order/record')
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
            login(True)
            return order_record(True)

        r.raise_for_status()
        
        re = json.loads(r.text)

        return re['data']

    except HTTPError as ex:
        return ex

# app.run()

# heroku login -i
# heroku git:remote -a sl-tg-bot
# git push heroku master
# heroku git:remote -a sl-tg-bot1
# git push heroku master
# heroku git:remote -a sl-tg-bot2
# git push heroku master
# heroku git:remote -a sl-tg-bot3
# git push heroku master

# heroku login -i
# heroku git:remote -a sl-tg-bot4
# git push heroku master
# heroku git:remote -a sl-tg-bot5
# git push heroku master