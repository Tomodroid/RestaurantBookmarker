# 初級で作ったアプリを再利用したものです。

# Web API 1つ目: HeartRails Geo API
# 公式URL: http://geoapi.heartrails.com/api.html
# エンドポイント: http://geoapi.heartrails.com/api/json

# Web API 2つ目: リクルートWebサービス グルメサーチAPI
# 公式URL: https://webservice.recruit.co.jp/doc/hotpepper/reference.html
# エンドポイント: https://webservice.recruit.co.jp/hotpepper/gourmet/v1

from flask import abort
import requests
import json

def get_station(mypost): # 郵便番号から最寄り駅データのjson入手
    url_post = 'http://geoapi.heartrails.com/api/json'
    param_post = {'method': 'getStations', 'postal': mypost}
    res_post = requests.get(url_post, params = param_post)
    json_post = json.loads(res_post.text)
    return json_post

class Station: # jsonに基づく駅オブジェクト作成
    def __init__(self, json_post):
        if 'error' in json_post['response']:
            abort(400)
        else:
            dict_post = json_post['response']['station'][0]
            self.station = dict_post['name']
            self.line = dict_post['line']
            self.longtitude = dict_post['x']
            self.latitude = dict_post['y']

def get_restaurant(longtitude, latitude): # 駅オブジェクトからレストランデータのjson入手
    url_gourmet = 'https://webservice.recruit.co.jp/hotpepper/gourmet/v1'
    param_gourmet = {'key': '5b54d842190292fa',
                    'lng': longtitude,
                    'lat': latitude,
                    'order': 4,
                    'range': 2,
                    'count': 50, 
                    'format': 'json'}
    res_gourmet = requests.get(url_gourmet, params = param_gourmet)
    json_gourmet = json.loads(res_gourmet.text)
    return json_gourmet