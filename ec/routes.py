# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 16:13:45 2021

@author: bruceyu1113
"""
from flask import jsonify,request,Blueprint
from datetime import datetime,date,timedelta
import pandas as pd
import pymysql
import sys
import os
import requests
import numpy as np

path1 = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, path1)
from cache import cache
import db_config
path2 = "C:/Users/Public/version_control/code/mart"
sys.path.insert(0, path2)
from Tag_NewContent import get_data
from Tag_Clustering_Hourly_Health import return_post
os.chdir(path2.replace('code','query')+'\\Tag_NewContent')


##宣告Blueprint route名稱##
ec = Blueprint('ec',__name__,url_prefix='/ec')
##

mysql = db_config.mysql


@ec.route('/ec')
def getdata():
    return{'health': 'value'}

@ec.route('/')
@cache.cached(timeout=5)
def home():
    return f'<h1>EC Recommend API</h1>'


@ec.route('/health_content')
def health_content():
    minute = datetime.now().minute
    table = cache.get('health_content')
    day = request.args.get('day', 1, type = int)
    if not table or (minute in [0,15,30,45]):
        content = get_data('health_content', 1080)
        table = content.to_json(force_ascii=False)
        cache.set('health_content',table,timeout=3600)
        filt_tmp = content[content['date']>=date.today() - timedelta(days=day)]
        filt_tmp = filt_tmp.drop(['date'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt
    else:
        content = pd.read_json(table)
        filt_tmp = content[content['date']>=date.today() - timedelta(days=day)]
        filt_tmp = filt_tmp.drop(['date'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt


@ec.route('/supertaste_content')
def supertaste_content():
    minute = datetime.now().minute
    table = cache.get('supertaste_content')
    day = request.args.get('day', 1, type = int)
    if not table or (minute in [0,15,30,45]):
        content = get_data('supertaste_content', 1080)
        table = content.to_json(force_ascii=False)
        cache.set('supertaste_content',table,timeout=3600)
        filt_tmp = content[content['date']>=date.today() - timedelta(days=day)]
        filt_tmp = filt_tmp.drop(['date'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt
    else:
        content = pd.read_json(table)
        filt_tmp = content[content['date']>=date.today() - timedelta(days=day)]
        filt_tmp = filt_tmp.drop(['date'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt
        return filt


@ec.route('/woman_content')
def woman_content():
    minute = datetime.now().minute
    table = cache.get('woman_content')
    day = request.args.get('day', 1, type = int)
    if not table or (minute in [0,15,30,45]):
        content = get_data('woman_content', 1080)
        table = content.to_json(force_ascii=False)
        cache.set('woman_content',table,timeout=3600)
        filt_tmp = content[content['date']>=date.today() - timedelta(days=day)]
        filt_tmp = filt_tmp.drop(['date'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt
    else:
        content = pd.read_json(table)
        filt_tmp = content[content['date']>=date.today() - timedelta(days=day)]
        filt_tmp = filt_tmp.drop(['date'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt


@ec.route('/ec_content')
def ec_content():
    minute = datetime.now().minute
    table = cache.get('ec_content')
    if not table or (minute in [0,15,30,45]):
        content = get_data('ec_content')
        table = content.to_json(force_ascii=False)
        cache.set('ec_content',table,timeout=3600)
        return table
    else:
        return table


@ec.route('/dict')
def dict():
    minute = datetime.now().minute
    table = cache.get('dict')
    domain = request.args.get('domain', '', type = str)
    if not table or (minute in [0,15,30,45]):
        content = get_data('dict')
        table = content.to_json(force_ascii=False)
        cache.set('dict',table,timeout=3600)
        filt_tmp = content[content['domain'].isin(domain.split(','))]
        filt_tmp = filt_tmp.drop(['domain'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt
    else:
        content = pd.read_json(table)
        filt_tmp = content[content['domain'].isin(domain.split(','))]
        filt_tmp = filt_tmp.drop(['domain'], axis=1)
        filt = filt_tmp.to_json(force_ascii=False)
        return filt


@ec.route('/recommend_list', methods=['GET'])
def result():
    minute = datetime.now().minute
    table = cache.get('recommend')
#        article_id = request.args.get('article_id', 1, type = int)
    if not table or (minute > 0 and minute <= 5) or (minute > 15 and minute <= 20) or (minute >= 30 and minute <= 35) or (minute >= 45 and minute <= 50):
        tmp = get_data('recommend_list',domain = 'Health')
        table = tmp.to_json(force_ascii=False)
#            cache.set('news_content_tmp',content,timeout=86100)
        cache.set('recommend',table,timeout=86100)
#            filt_tmp = tmp[tmp['article_id']==article_id]
#            filt_tmp = filt_tmp.drop(['article_id'], axis=1)
#            filt = filt_tmp.to_json(force_ascii=False)
        return table
    else:
#            tmp = pd.read_json(table)
#            filt_tmp = tmp[tmp['article_id']==article_id]
#            filt_tmp = filt_tmp.drop(['article_id'], axis=1)
#            filt = filt_tmp.to_json(force_ascii=False)
        return table



@ec.route('/post_recommend',methods=['POST'])##News 推薦文章API
def return_recommend():
    temp_json = request.get_json(force=True)
    recommend_list = return_post(temp_json['text'])
#        for index, row in new_record_recom_nid.iterrows():
#            #result[index] = row.to_json()
#            result[index] = dict(row)
#        result = new_record_recom_nid[['recom_nid']].to_dict('r')[0]
    return jsonify(recommend_list)


##error message
@ec.app_errorhandler(404)
def not_found(e):
#    health.logger.error(f"not found:{e},route:{request.url}")
    error_message = e
    requests.get(f"http://34.80.91.60:8020/LineNotify-news-error?ip_address={request.remote_addr}&message={error_message}&request_url={request.url}")
    message={
            'status':404,
            'message': 'not found ' + request.url
            }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@ec.app_errorhandler(500)
def server_error(e):
#    health.logger.error(f"Server error:{e},route:{request.url}")
    error_message = e
    requests.get(f"http://34.80.91.60:8020/LineNotify-news-error?ip_address={request.remote_addr}&message={error_message}&request_url={request.url}")
    message={
            'status':500,
            'message': 'server error ' + request.url
            }
    resp = jsonify(message)
    resp.status_code = 500
    return resp

@ec.app_errorhandler(403)
def forbidden(e):
#    health.logger.error(f"Forbidden access:{e},route:{request.url}")
    error_message = e
    requests.get(f"http://34.80.91.60:8020/LineNotify-news-error?ip_address={request.remote_addr}&message={error_message}&request_url={request.url}")
    message={
            'status':403,
            'message': 'server error ' + request.url
            }
    resp = jsonify(message)
    resp.status_code = 403
    return resp