# -*- coding: utf-8 -*-

__author__ = 'yangyuenan'

from datetime import datetime, timedelta
from flask import request
from flask_login import login_required
from . import api
from app.api.controller import get_item_echarts, index_echarts
from app.models import CfgNotify, MonitorItem, HostInfo, db


MODEL_DICT = {'notifies': CfgNotify,
              'items': MonitorItem
              }


# 图表接口
@api.route('/api/pyecharts', methods=['POST'])
@login_required
def echarts():
    return {'myecharts': get_item_echarts(request)}


# 检查项、报警联系人生效/失效接口
@api.route('/api/<path:url>', methods=['PUT'])
@login_required
def notifies(url):
    if request.method == 'PUT':
        info = url.split('/')
        status = True if info[3] == 'true' else False
        model = MODEL_DICT.get(info[0])
        item = model.get(model.id == info[1])
        item.status = status
        item.save()
    return 'complete'


# 首页统计数据接口
@api.route('/api/stats/summary', methods=['GET'])
@login_required
def index_count():
    host_count = HostInfo.select().count()
    item_count = MonitorItem.select().count()
    danger_count = MonitorItem.select().where(MonitorItem.item_status == 0).count()
    count = {'host_count': host_count,
             'item_count': item_count,
             'danger_count': danger_count}
    return count


# 首页主机报警统计图表接口
@api.route('/api/host/warning', methods=['GET'])
@login_required
def host_warning():
    start_time = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_time = datetime.now().strftime('%Y-%m-%d')
    sql = """
    SELECT a._date, count(1) from (SELECT DATE_FORMAT(check_time,'%Y-%m-%d') as _date, 
    host_name FROM itemstatus WHERE check_time > '{start_time}' and check_time < '{end_time}' and warning_status=1 
    GROUP BY _date,host_name ORDER BY _date) a GROUP BY _date""".format(start_time=start_time, end_time=end_time)
    cursor = db.cursor()
    cursor.execute(sql)
    host_count = cursor.fetchall()
    db.close()
    date_list = [data[0] for data in host_count]
    count_list = [data[1] for data in host_count]
    return {'myecharts': index_echarts('host', date_list, count_list)}


# 首页项目报警统计图表接口
@api.route('/api/item/warning', methods=['GET'])
@login_required
def item_warning():
    start_time = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    end_time = datetime.now().strftime('%Y-%m-%d')
    sql = """
    SELECT a._date, count(1) from (SELECT DATE_FORMAT(check_time,'%Y-%m-%d') as _date, 
    item_id FROM itemstatus WHERE check_time > '{start_time}' and check_time < '{end_time}' and warning_status=1 
    GROUP BY _date,item_id ORDER BY _date) a GROUP BY _date""".format(start_time=start_time, end_time=end_time)
    cursor = db.cursor()
    cursor.execute(sql)
    item_count = cursor.fetchall()
    db.close()
    date_list = [data[0] for data in item_count]
    count_list = [data[1] for data in item_count]
    return {'myecharts': index_echarts('item', date_list, count_list)}

