# -*- coding: utf-8 -*-

__author__ = 'yangyuenan'

from datetime import datetime, timedelta
from flask import request
from flask_login import login_required
from pyecharts.charts import Grid, Line
from pyecharts import options as opts
from . import api
from app.utils import utils
from app.models import CfgNotify, MonitorItem, HostInfo, ItemStatus, db


MODEL_DICT = {'notifies': CfgNotify,
              'items': MonitorItem
              }


# 获取项目状态图表
def get_item_echarts(rq):
    if rq.method == 'POST':
        status_list = []
        rx_speed_list = []
        tx_speed_list = []
        date_list = []
        avg_list = []
        avg_rx_list = []
        avg_tx_list = []
        item_id = rq.form.get('item_id')
        date_ware = rq.form.get('date_ware')
        warning_value = rq.form.get('warning_value')
        start_date, end_date = date_ware.split('-')
        query = ItemStatus.select(ItemStatus.item_name, ItemStatus.check_time, ItemStatus.item_detail).where(
            ItemStatus.item_id == item_id, ItemStatus.check_time <= end_date + ' 23:59:59',
            ItemStatus.check_time >= start_date).order_by(ItemStatus.check_time.asc()).dicts()
        if datetime.strptime(end_date.strip(), '%Y/%m/%d') - timedelta(days=2) < datetime.strptime(start_date.strip(), '%Y/%m/%d'):
            date_time = query[0]['check_time'].strftime('%Y-%m-%d %H')
            for data in query:
                check_time = data['check_time'].strftime('%Y-%m-%d %H')
                status = utils.str_to_dict(data['item_detail'])
                if date_time == check_time:
                    if 'status' in status:
                        status_list.append(status.get('status'))
                    else:
                        rx_speed_list.append(status.get('rx_speed'))
                        tx_speed_list.append(status.get('tx_speed'))
                else:
                    if status_list:
                        avg_list.append(sum(status_list) / len(status_list))
                        status_list = [status.get('status')]
                    else:
                        avg_rx_list.append(sum(rx_speed_list) / len(rx_speed_list))
                        avg_tx_list.append(sum(tx_speed_list) / len(tx_speed_list))
                        rx_speed_list = [status.get('rx_speed')]
                        tx_speed_list = [status.get('tx_speed')]
                    date_list.append(date_time)
                    date_time = check_time
        else:
            date_time = query[0]['check_time'].strftime('%Y-%m-%d')
            for data in query:
                check_time = data['check_time'].strftime('%Y-%m-%d')
                status = utils.str_to_dict(data['item_detail'])
                if date_time == check_time:
                    if status.get('status'):
                        status_list.append(status.get('status'))
                    else:
                        rx_speed_list.append(status.get('rx_speed'))
                        tx_speed_list.append(status.get('tx_speed'))
                else:
                    if status_list:
                        avg_list.append(sum(status_list) / len(status_list))
                        status_list = [status.get('status')]
                    else:
                        avg_rx_list.append(sum(rx_speed_list) / len(rx_speed_list))
                        avg_tx_list.append(sum(tx_speed_list) / len(tx_speed_list))
                        rx_speed_list = [status.get('rx_speed')]
                        tx_speed_list = [status.get('tx_speed')]
                    date_list.append(date_time)
                    date_time = check_time
        date_list.append(date_time)
        if status_list:
            avg_list.append(sum(status_list) / len(status_list))
        else:
            avg_rx_list.append(sum(rx_speed_list) / len(rx_speed_list))
            avg_tx_list.append(sum(tx_speed_list) / len(tx_speed_list))
        return draw_echarts(query[0].get('item_name'), warning_value, date_list, avg_list, avg_rx_list, avg_tx_list)


def format_num(num):
    return round(num, 2)


# 绘制echarts图表
def draw_echarts(item_name, warning_value, date_list, avg_list=[], avg_rx_list=[], avg_tx_list=[]):
    assert isinstance(avg_list, list)
    assert isinstance(avg_rx_list, list)
    assert isinstance(avg_tx_list, list)

    area = Line()
    area.add_xaxis(date_list)
    if avg_list:
        area.add_yaxis("使用率（%）", [data for data in map(format_num, avg_list)], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    else:
        area.add_yaxis("rx（接收速率KB/s）", [data for data in map(format_num, avg_rx_list)], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
        area.add_yaxis("tx（发送速率KB/s）", [data for data in map(format_num, avg_tx_list)], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    area.set_global_opts(title_opts=opts.TitleOpts(title=item_name, pos_left="10%"),
                         legend_opts=opts.LegendOpts(pos_left="30%"))
    area.set_series_opts(
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(y=warning_value, name='基准值')]
        )
    )

    grid = Grid(init_opts=opts.InitOpts(width="100%"))
    grid.add(area, grid_opts=opts.GridOpts())
    return grid.render_embed()


# 绘制首页图表
def index_echarts(type, date_list, count_list):
    assert isinstance(date_list, list)
    assert isinstance(count_list, list)

    line = Line()
    line.add_xaxis(date_list)
    line.add_yaxis('{type}报警数量统计'.format(type=type), count_list)
    line.set_global_opts(legend_opts=opts.LegendOpts(pos_left="30%"))
    grid = Grid(init_opts=opts.InitOpts(width="100%"))
    grid.add(line, grid_opts=opts.GridOpts())
    return grid.render_embed()


# 图标接口
@api.route('/api/pyecharts', methods=['POST'])
@login_required
def echarts():
    return {'myecharts': get_item_echarts(request)}


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

