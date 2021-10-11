# -*- coding: utf-8 -*-

__author__ = 'yangyuenan'
__time__ = '2021/5/2 18:53'


from datetime import datetime, timedelta
from pyecharts.charts import Grid, Line
from pyecharts import options as opts
from app.utils import utils
from app.models import ItemStatus


# 获取项目状态图表
# def get_item_echarts(rq):
#     if rq.method == 'POST':
#         status_list = []
#         rx_speed_list = []
#         tx_speed_list = []
#         date_list = []
#         avg_list = []
#         avg_rx_list = []
#         avg_tx_list = []
#         item_id = rq.form.get('item_id')
#         date_ware = rq.form.get('date_ware')
#         warning_value = rq.form.get('warning_value')
#         start_date, end_date = date_ware.split('-')
#         query = ItemStatus.select(ItemStatus.item_name, ItemStatus.check_time, ItemStatus.item_detail).where(
#             ItemStatus.item_id == item_id, ItemStatus.check_time <= end_date + ' 23:59:59',
#             ItemStatus.check_time >= start_date).order_by(ItemStatus.check_time.asc()).dicts()
#         if datetime.strptime(end_date.strip(), '%Y/%m/%d') - timedelta(days=2) < datetime.strptime(start_date.strip(), '%Y/%m/%d'):
#             date_time = query[0]['check_time'].strftime('%Y-%m-%d %H')
#             for data in query:
#                 check_time = data['check_time'].strftime('%Y-%m-%d %H')
#                 status = utils.str_to_dict(data['item_detail'])
#                 if date_time == check_time:
#                     if 'status' in status:
#                         status_list.append(status.get('status'))
#                     else:
#                         rx_speed_list.append(status.get('rx_speed'))
#                         tx_speed_list.append(status.get('tx_speed'))
#                 else:
#                     if status_list:
#                         avg_list.append(sum(status_list) / len(status_list))
#                         status_list = [status.get('status')]
#                     else:
#                         avg_rx_list.append(sum(rx_speed_list) / len(rx_speed_list))
#                         avg_tx_list.append(sum(tx_speed_list) / len(tx_speed_list))
#                         rx_speed_list = [status.get('rx_speed')]
#                         tx_speed_list = [status.get('tx_speed')]
#                     date_list.append(date_time)
#                     date_time = check_time
#         else:
#             date_time = query[0]['check_time'].strftime('%Y-%m-%d')
#             for data in query:
#                 check_time = data['check_time'].strftime('%Y-%m-%d')
#                 status = utils.str_to_dict(data['item_detail'])
#                 if date_time == check_time:
#                     if status.get('status'):
#                         status_list.append(status.get('status'))
#                     else:
#                         rx_speed_list.append(status.get('rx_speed'))
#                         tx_speed_list.append(status.get('tx_speed'))
#                 else:
#                     if status_list:
#                         avg_list.append(sum(status_list) / len(status_list))
#                         status_list = [status.get('status')]
#                     else:
#                         avg_rx_list.append(sum(rx_speed_list) / len(rx_speed_list))
#                         avg_tx_list.append(sum(tx_speed_list) / len(tx_speed_list))
#                         rx_speed_list = [status.get('rx_speed')]
#                         tx_speed_list = [status.get('tx_speed')]
#                     date_list.append(date_time)
#                     date_time = check_time
#         date_list.append(date_time)
#         if status_list:
#             avg_list.append(sum(status_list) / len(status_list))
#         else:
#             avg_rx_list.append(sum(rx_speed_list) / len(rx_speed_list))
#             avg_tx_list.append(sum(tx_speed_list) / len(tx_speed_list))
#         return draw_echarts(query[0].get('item_name'), warning_value, date_list, avg_list, avg_rx_list, avg_tx_list)


# 获取项目状态图表
def get_item_echarts(rq):
    if rq.method == 'POST':
        status_list = []
        rx_speed_list = []
        tx_speed_list = []
        date_list = []
        item_id = rq.form.get('item_id')
        date_ware = rq.form.get('date_ware')
        warning_value = rq.form.get('warning_value')
        start_date, end_date = date_ware.split('-')
        query = ItemStatus.select(ItemStatus.item_name, ItemStatus.check_time, ItemStatus.item_detail).where(
            ItemStatus.item_id == item_id, ItemStatus.check_time <= end_date + ' 23:59:59',
            ItemStatus.check_time >= start_date).order_by(ItemStatus.check_time.asc()).dicts()
        for data in query:
            status = utils.str_to_dict(data['item_detail'])
            date_list.append(data['check_time'])
            if 'status' in status:
                status_list.append(status.get('status'))
            else:
                rx_speed_list.append(status.get('rx_speed'))
                tx_speed_list.append(status.get('tx_speed'))
        return draw_echarts(query[0].get('item_name'), warning_value, date_list, status_list, rx_speed_list, tx_speed_list)


def format_num(num):
    return round(num, 2)


# 绘制echarts图表
def draw_echarts(item_name, warning_value, date_list, status_list=[], rx_speed_list=[], tx_speed_list=[]):
    assert isinstance(status_list, list)
    assert isinstance(rx_speed_list, list)
    assert isinstance(tx_speed_list, list)

    area = Line()
    area.add_xaxis(date_list)
    if status_list:
        area.add_yaxis("使用率（%）", [data for data in map(format_num, status_list)], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    else:
        area.add_yaxis("rx（接收速率KB/s）", [data for data in map(format_num, rx_speed_list)], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
        area.add_yaxis("tx（发送速率KB/s）", [data for data in map(format_num, tx_speed_list)], areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
    area.set_global_opts(title_opts=opts.TitleOpts(title=item_name, pos_left="10%"),
                         legend_opts=opts.LegendOpts(pos_left="30%"))
    area.set_series_opts(
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(y=warning_value, name='基准值')]
        )
    )
    if len(date_list) > 20:
        area.set_global_opts(datazoom_opts=opts.DataZoomOpts(range_start=10, range_end=30))

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
