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
import read_gzip
import db_config
import tag_recom_algorithm as tra
import articleRecomTag as tagrec
from df_to_json import dataframe_to_json
path2 = "C:/Users/Public/version_control/code/mart"
sys.path.insert(0, path2)
from Tag_NewContent import get_data
from Tag_Clustering_Hourly_Health import return_post
os.chdir(path2.replace('code','query')+'\\Tag_NewContent')


##宣告Blueprint route名稱##
supertaste = Blueprint('supertaste',__name__,url_prefix='/supertaste')
##

mysql = db_config.mysql


@supertaste.route('/getdata')
def getdata():
    return{'supertaste': 'value'}

@supertaste.route('/')
@cache.cached(timeout=5)
def home():
    return f'<h1>Health Recommend API</h1>'


@supertaste.route('/content')
def content():
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


@supertaste.route('/content_update')
def content_update():
    minute = datetime.now().minute
    table = cache.get('supertaste_update')
    if not table or (minute in [0,15,30,45]):
        content = get_data('supertaste_update', 1080)
        table = content.to_json(force_ascii=False)
        cache.set('supertaste_update',table,timeout=3600)
        return table
    else:
        return table

@supertaste.route('/article_cache', methods=['GET'])##後台文章API
def health_article_cache():
    args = request.args
#            now = datetime.now()
    hour = datetime.now().hour
    minute = datetime.now().minute
    day = args.get('day') if 'day' in args else 90
    health_table = cache.get('supertaste_cache_'+str(day))
    if day ==90:
        if not health_table or \
        ((hour>0 and minute > 0) and (hour>0 and minute <= 1)) or ((hour>6 and minute > 0) and (hour>6 and minute <= 1)) or \
        ((hour>8 and minute > 0) and (hour>8 and minute <= 1)) or ((hour>10 and minute > 0) and (hour>10 and minute <= 1)) or \
        ((hour>12 and minute > 0) and (hour>12 and minute <= 1)) or ((hour>14 and minute > 0) and (hour>14 and minute <= 1)) or \
        ((hour>16 and minute > 0) and (hour>16 and minute <= 1)) or ((hour>18 and minute > 0) and (hour>18 and minute <= 1)) or \
        ((hour>20 and minute > 0) and (hour>20 and minute <= 1)) or ((hour>22 and minute > 0) and (hour>22 and minute <= 1)):
#                if not news_table or(now_time >= time(00,0) and now_time <= time(00,2)) :
            db_config.aws_db()
            insert = """SELECT id AS nid,
                        title AS title,
                        keyword AS tag,
                        cast(DATE(publish)as char) AS date
                        FROM tvbs_v4.eatdrink_articles
                        WHERE DATE(publish) >= SUBDATE(CURDATE(), INTERVAL 90 DAY)
                        AND DATE(publish) <= CURDATE()
                        AND status = 1;"""
            print('Not cache')
            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(insert)
            rows = cur.fetchall()
            health_table=jsonify(rows)
            health_table.status_code=200
            cache.set('supertaste_cache_'+str(day),health_table,timeout=7200)
            cur.close()
            conn.close()
            return health_table
        else:
            print('the day is 90 and health_caches')
            return health_table
    else:
        if not health_table:
            print('Not cache')
            db_config.aws_db()
            insert = """SELECT id AS nid,
                        title AS title,
                        keyword AS tag,
                        cast(DATE(publish)as char) AS date
                        FROM tvbs_v4.eatdrink_articles
                        WHERE DATE(publish) >= SUBDATE(CURDATE(), INTERVAL %s DAY)
                        AND DATE(publish) <= CURDATE()
                        AND status = 1;""" % (day)
            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(insert)
            rows = cur.fetchall()
            health_table=jsonify(rows)
            health_table.status_code=200
            cache.set('supertaste_cache_'+str(day),health_table,timeout=3600)
            cur.close()
            conn.close()
            return health_table
        else:
            print('supertaste_cache_')
            return health_table


@supertaste.route('/tag_score_table', methods=['GET'])##News 標籤推薦API
#    @cache.cached(timeout=5)
def tvbs_news_tag_analysis():
    hour = datetime.now().hour
    minute = datetime.now().minute
#    args = request.args
    search_console = request.args.get('gsc', 'Y', type = str)
    day = request.args.get('day',90 , type = int)
    tag_summary_list = cache.get('supertaste_tag_cache_tag_cache'+str(day)+search_console)
    try:
        if (not tag_summary_list) or\
            ((hour>0 and minute > 0) and (hour>0 and minute <= 1)) or ((hour>6 and minute > 0) and (hour>6 and minute <= 1)) or \
            ((hour>8 and minute > 0) and (hour>8 and minute <= 1)) or ((hour>10 and minute > 0) and (hour>10 and minute <= 1)) or \
            ((hour>12 and minute > 0) and (hour>12 and minute <= 1)) or ((hour>14 and minute > 0) and (hour>14 and minute <= 1)) or \
            ((hour>16 and minute > 0) and (hour>16 and minute <= 1)) or ((hour>18 and minute > 0) and (hour>18 and minute <= 1)) or \
            ((hour>20 and minute > 0) and (hour>20 and minute <= 1)) or ((hour>22 and minute > 0) and (hour>22 and minute <= 1)):
#            if (not news_tag_summary):
            print('Not cache')
            back_tag_of_dfItem = tra.cache_article_table('supertaste').get_aws_table_cache(day)
            if search_console =='Y':
                tag_summary = tra.editorTag('supertaste',back_tag_of_dfItem,'Y').editor_tag_summary()
            else:
                tag_summary = tra.editorTag('supertaste',back_tag_of_dfItem,'N').editor_tag_summary()
            summary_list = dataframe_to_json(tag_summary)
            tag_summary_list = jsonify(summary_list)
            tag_summary_list.status_code=200
            cache.set('supertaste_tag_cache_tag_cache'+str(day)+search_console,tag_summary_list,timeout=7200)
            return tag_summary_list
        else:
            print('supertaste_tag_cache_tag_cache')
            return tag_summary_list
    finally:
        print('request get /tvbs_health_tag_analysis')

@supertaste.route('/google_scarch_console_tag',methods =['GET'])
def gsc_tag():
    hour = datetime.now().hour
    minute = datetime.now().minute
    gsc_table = cache.get('supertaste_tag_cache')
    if not gsc_table or \
        ((hour>0 and minute > 0) and (hour>0 and minute <= 1)) or ((hour>6 and minute > 0) and (hour>6 and minute <= 1)) or \
        ((hour>8 and minute > 0) and (hour>8 and minute <= 1)) or ((hour>10 and minute > 0) and (hour>10 and minute <= 1)) or \
        ((hour>12 and minute > 0) and (hour>12 and minute <= 1)) or ((hour>14 and minute > 0) and (hour>14 and minute <= 1)) or \
        ((hour>16 and minute > 0) and (hour>16 and minute <= 1)) or ((hour>18 and minute > 0) and (hour>18 and minute <= 1)) or \
        ((hour>20 and minute > 0) and (hour>20 and minute <= 1)) or ((hour>22 and minute > 0) and (hour>22 and minute <= 1)):
        tag_gsc = read_gzip.tmp_read('dict','supertaste')
        tag_gsc['search_content'] = tag_gsc["search_content"].map(lambda tag: tag.replace(' ',','))
        tag_gsc['search_content'].replace('', np.nan, inplace=True)
        tag_gsc = tag_gsc.dropna(how = 'all')
        tag_gsc = tag_gsc.reset_index().rename(columns={tag_gsc.index.name:'nid'})
        gsc_list = dataframe_to_json(tag_gsc)
        gsc_table = jsonify(gsc_list)
        gsc_table.status_code=200
        cache.set('supertaste_tag_cache',gsc_table,timeout=7200)
        return gsc_table
    else:
        print('supertaste_tag_cache')
        return gsc_table


@supertaste.route('/post_tag_recommend',methods=['POST'])##News 推薦文章API
def tvbs_tag_recommend():
    result={}
    temp_json  = request.get_json(force=True)
    tag_recommentTop20 = tagrec.get_tag_recommend('supertaste',temp_json['article'],'Y')
    result = {'recomment_tag':tag_recommentTop20}
    return jsonify(result)

@supertaste.route('/tags', methods=['GET'])
def tags():
#        now = datetime.now()
#        now_time = now.time()
    table = cache.get('tag')
    if not table:
        tmp = get_data('tags')
        table = tmp.to_json(force_ascii=False)
#            cache.set('news_content_tmp',content,timeout=86100)
        cache.set('tag',table,timeout=86100)
        return table
    else:
        return table


@supertaste.route('/gsc', methods=['GET'])
def gsc():
#        now = datetime.now()
#        now_time = now.time()
    table = cache.get('gsc')
    if not table:
        tmp = get_data('gsc', domain = 'Health')
        table = tmp.to_json(force_ascii=False)
#            cache.set('news_content_tmp',content,timeout=86100)
        cache.set('gsc',table,timeout=86100)
        return table
    else:
        return table


@supertaste.route('/recommend_list', methods=['GET'])
def result():
    minute = datetime.now().minute
    table = cache.get('recommend')
#        article_id = request.args.get('article_id', 1, type = int)
    if not table or (minute > 0 and minute <= 5) or (minute > 15 and minute <= 20) or (minute >= 30 and minute <= 35) or (minute >= 45 and minute <= 50):
        tmp = get_data('recommend_list',domain = 'Supertaste')
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



@supertaste.route('/post_recommend',methods=['POST'])##News 推薦文章API
def return_recommend():
    temp_json = request.get_json(force=True)
    recommend_list = return_post(temp_json['text'])
#        for index, row in new_record_recom_nid.iterrows():
#            #result[index] = row.to_json()
#            result[index] = dict(row)
#        result = new_record_recom_nid[['recom_nid']].to_dict('r')[0]
    return jsonify(recommend_list)


##error message
@supertaste.app_errorhandler(404)
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

@supertaste.app_errorhandler(500)
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

@supertaste.app_errorhandler(403)
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