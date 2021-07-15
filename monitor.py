#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import base64
import requests
from datetime import datetime
from time import sleep
from peewee import fn
from app import get_logger
from app.utils import SFTP, telnet, mail, dict_to_str, query_to_list, str_to_dict
from app.models import HostInfo, ItemStatus, MonitorItem, CfgNotify, GlobalCfg, db
from conf.config import config

logger = get_logger(__name__)
CFG = config[os.getenv('FLASK_CONFIG') or 'default']

NORMAL_STATUS = {
    'item_status': 1,
    'warning_status': 0
}

ABNORMAL_STATUS = {
    'item_status': 0,
    'warning_status': 1
}

LAST_NET_INFO = {}


def auto_manager_db(func):
    def wrapper(*args, **kwargs):
        db.connect()
        result = func(*args, **kwargs)
        db.close()
        return result
    return wrapper


# 获取配置
@auto_manager_db
def get_cfg(is_warning=False):
    if is_warning:
        warning_user = query_to_list(CfgNotify.select().where(CfgNotify.status == 1).dicts())
        return warning_user
    else:
        conf = GlobalCfg.select().dicts()[0]
        interval_time = conf.get('inspect_interval', 0) * 60 or 300
        inspect_item = query_to_list(
            MonitorItem.select(MonitorItem, HostInfo).join(HostInfo).where(MonitorItem.status == 1).order_by(
                HostInfo.host_name.asc(),
                MonitorItem.id.asc()).dicts())
        return interval_time, inspect_item, conf


def get_cpu_used(item, inspect_info):
    assert isinstance(item, dict)
    assert isinstance(inspect_info, list)

    monitor_item_detail = 'cpu使用率：{cpu}%'.format(cpu=inspect_info[0])
    status_item_detail = {'status': float(inspect_info[0])}
    item_detail = {'monitor_item_detail': monitor_item_detail, 'status_item_detail': status_item_detail}
    status = NORMAL_STATUS if float(inspect_info[0]) <= float(item['warning_value']) else ABNORMAL_STATUS
    return item_detail, status


def get_mem_used(item, inspect_info):
    assert isinstance(item, dict)
    assert isinstance(inspect_info, list)

    monitor_item_detail = '内存使用率：{mem}%'.format(mem=inspect_info[1][:5])
    status_item_detail = {'status': float(inspect_info[1][:5])}
    item_detail = {'monitor_item_detail': monitor_item_detail, 'status_item_detail': status_item_detail}
    status = NORMAL_STATUS if float(inspect_info[1][:5]) <= float(item['warning_value']) else ABNORMAL_STATUS
    return item_detail, status


def get_disk_used(item, inspect_info):
    assert isinstance(item, dict)
    assert isinstance(inspect_info, list)

    disk_info = inspect_info[2].split(' ')
    monitor_item_detail = '已使用最多的分区为：{part}，使用率：{disk}'.format(part=disk_info[1], disk=disk_info[0])
    status_item_detail = {'status': float(disk_info[0][:-1])}
    item_detail = {'monitor_item_detail': monitor_item_detail, 'status_item_detail': status_item_detail}
    status = NORMAL_STATUS if float(disk_info[0][:-1]) <= float(item['warning_value']) else ABNORMAL_STATUS
    return item_detail, status


def get_net_used(item, inspect_info):
    assert isinstance(item, dict)
    assert isinstance(inspect_info, list)

    rx = float(inspect_info[3])
    tx = float(inspect_info[4])
    current_net_info = {'time': datetime.now(), 'rx': rx, 'tx': tx}
    last_net_info = LAST_NET_INFO.get(item['host_name'], {})
    if not last_net_info:
        net_info = ItemStatus.select(ItemStatus.check_time, ItemStatus.item_detail).where(
            ItemStatus.item_id == item['id'],
            ItemStatus.check_time == ItemStatus.select(fn.max(ItemStatus.check_time)).where(
                ItemStatus.item_id == item['id'])).dicts()
        if net_info:
            check_time = net_info[0]['check_time']
            detail = str_to_dict(net_info[0]['item_detail'])
            last_net_info = {'time': check_time,
                             'rx': detail['rx'],
                             'tx': detail['tx']}

    if last_net_info:
        interval_time = (current_net_info['time'] - last_net_info['time']).total_seconds()
        rx_speed = int((current_net_info['rx'] - last_net_info['rx']) / interval_time)
        tx_speed = int((current_net_info['tx'] - last_net_info['tx']) / interval_time)

        monitor_item_detail = '当前接收数据（KB）：{rx}，当前发送数据（KB）：{tx}，数据平均接收速率（KB/s）：{rx_speed}，数据平均发送速率（KB/s）：{tx_speed}'.format(
            rx=rx,
            tx=tx,
            rx_speed=rx_speed,
            tx_speed=tx_speed)
        status_item_detail = {'rx': rx, 'tx': tx, 'rx_speed': rx_speed, 'tx_speed': tx_speed}
        status = NORMAL_STATUS if float(rx_speed) <= float(item['warning_value']) and float(tx_speed) <= float(
            item['warning_value']) else ABNORMAL_STATUS
    else:
        monitor_item_detail = '当前接收数据（KB）：{rx}，当前发送数据（KB）：{tx}，数据平均接收速率（KB/s）：{rx_speed}，数据平均发送速率（KB/s）：{tx_speed}'.format(
            rx=rx,
            tx=tx,
            rx_speed=0,
            tx_speed=0)
        status = NORMAL_STATUS
        status_item_detail = {'rx': rx, 'tx': tx, 'rx_speed': 0, 'tx_speed': 0}
    item_detail = {'monitor_item_detail': monitor_item_detail, 'status_item_detail': status_item_detail}
    LAST_NET_INFO[item['host_name']] = current_net_info
    return item_detail, status


def get_tcp_info(item, inspect_info):
    assert isinstance(item, dict)
    assert isinstance(inspect_info, list)

    tcp_ip = item['host_ip']
    tcp_port = item['tcp_http']
    tcp_info = telnet(tcp_ip, tcp_port, timeout=3)
    monitor_item_detail = '端口连接成功' if not tcp_info else tcp_info
    status_item_detail = {'status': 1} if not tcp_info else {'status': 0}
    item_detail = {'monitor_item_detail': monitor_item_detail, 'status_item_detail': status_item_detail}
    status = NORMAL_STATUS if not tcp_info else ABNORMAL_STATUS
    return item_detail, status


def get_http_info(item, inspect_info):
    assert isinstance(item, dict)
    assert isinstance(inspect_info, list)

    http_url = item['tcp_http']
    try:
        http_info = requests.get(http_url)
        monitor_item_detail = '{status_code}，服务工作正常'.format(
            status_code=http_info.status_code) if http_info.status_code == 200 and item[
            'matching_char'] in http_info.text else str(http_info.status_code) + '，' + http_info.text
        status_item_detail = {'status': 1} if http_info.status_code == 200 and item[
            'matching_char'] in http_info.text else {'status': 0}

        item_detail = {'monitor_item_detail': monitor_item_detail, 'status_item_detail': status_item_detail}
        status = NORMAL_STATUS if http_info.status_code == 200 and item[
            'matching_char'] in http_info.text else ABNORMAL_STATUS
    except Exception as e:
        monitor_item_detail = str(e)
        status_item_detail = {'status': 0}
        item_detail = {'monitor_item_detail': monitor_item_detail, 'status_item_detail': status_item_detail}
        status = ABNORMAL_STATUS
    return item_detail, status


ITEM_DICT = {
    'cpu': get_cpu_used,
    '内存': get_mem_used,
    '硬盘': get_disk_used,
    '网络': get_net_used,
    'tcp服务': get_tcp_info,
    'http服务': get_http_info
}


# 保存检查结果
@auto_manager_db
def save_result(item, inspect_info):
    assert isinstance(item, dict)
    assert isinstance(inspect_info, bytes)

    item_detail, status = ITEM_DICT.get(item['item_type'])(item, str(inspect_info, encoding='utf-8').split('\n'))

    # 更新监控项状态
    monitor_item = MonitorItem.get(MonitorItem.id == item['id'])
    monitor_item.check_time = datetime.now()
    monitor_item.item_detail = item_detail['monitor_item_detail']
    monitor_item.item_status = status['item_status']
    monitor_item.save()

    item_result = ItemStatus(host_name=item['host_name'], host_ip=item['host_ip'], item_id=item['id'],
                             item_name=item['item_name'], check_time=datetime.now(),
                             item_detail=dict_to_str(item_detail['status_item_detail']),
                             warning_status=status['warning_status'])
    item_result.save()
    return item_detail, status


# 守护进程
def daemonize():
    """
    创建守护进程
    :return:
    """
    import sys
    # 从父进程fork一个子进程出来
    pid = os.fork()
    # 子进程的pid一定为0，父进程大于0
    if pid:
        # 退出父进程，sys.exit()方法比os._exit()方法会多执行一些刷新缓冲工作
        sys.exit(0)

    # 子进程默认继承父进程的工作目录，最好是变更到根目录，否则回影响文件系统的卸载
    os.chdir('/')
    # 子进程默认继承父进程的umask（文件权限掩码），重设为0（完全控制），以免影响程序读写文件
    os.umask(0)
    # 让子进程成为新的会话组长和进程组长
    os.setsid()

    # 注意了，这里是第2次fork，也就是子进程的子进程，我们把它叫为孙子进程
    _pid = os.fork()
    if _pid:
        # 退出子进程
        sys.exit(0)

    # 此时，孙子进程已经是守护进程了，接下来重定向标准输入、输出、错误的描述符(是重定向而不是关闭, 这样可以避免程序在 print 的时候出错)

    # 刷新缓冲区先，小心使得万年船
    sys.stdout.flush()
    sys.stderr.flush()

    # dup2函数原子化地关闭和复制文件描述符，重定向到/dev/nul，即丢弃所有输入输出
    with open('/dev/null') as read_null, open('/dev/null', 'w') as write_null:
        os.dup2(read_null.fileno(), sys.stdin.fileno())
        os.dup2(write_null.fileno(), sys.stdout.fileno())
        os.dup2(write_null.fileno(), sys.stderr.fileno())


# 通知报警
def notice(warning_str, notify_user, conf):
    if warning_str:
        mail_list = []
        phone_list = []
        warning_user_list = get_cfg(is_warning=True)
        if warning_user_list and conf.get('id'):
            notify = notify_user.split('|')
            for user in warning_user_list:
                if notify[0] == 'all' or user['notify_name'] in notify:
                    if user['notify_type'] == 'MAIL':
                        mail_list.append(user['notify_number'])
                    elif user['notify_type'] == 'SMS':
                        phone_list.append(user['notify_number'])
            if mail_list:
                mail(smtpServer=conf['smtp_server'], smtpPort=conf['smtp_port'],loginUser=conf['smtp_user'],
                     loginPassword=str(base64.b64decode(conf['smtp_password_base64']), encoding='utf-8'),
                     mailFrom=conf['smtp_user'], mailTo=';'.join(mail_list), mailReceivers=mail_list,
                     mailSubject='opsmonitor监控报警', mailText=warning_str)
                logger.info('邮件已发送给{mail_to}'.format(mail_to=';'.join(mail_list)))


# 开始检查
def inspect(inspect_item, conf):
    host_name = None
    inspect_info = None
    for item in inspect_item:
        if not item['host_name'] == host_name:
            ssh = SFTP(ip=item['host_ip'], port=item['host_port'], user=item['host_user'],
                       password=str(base64.b64decode(item['host_password_base64']), encoding='utf-8'))
            ssh.ssh_open()
            inspect_info = ssh.ssh_execute(CFG.SSH_CMD_7)
            if len(inspect_info) < 6:
                inspect_info = ssh.ssh_execute(CFG.SSH_CMD_6)
            ssh.close()
            host_name = item['host_name']
        item_detail, status = save_result(item, inspect_info)
        if status['warning_status']:
            warning_str = '主机:{host_name}\n监控项：{item_name}异常\n详细信息：{item_detail}\n时间：{inspect_time}\n\n\n'.format(
                host_name=item['host_name'], item_name=item['item_name'],
                item_detail=item_detail['monitor_item_detail'], inspect_time=datetime.now())
            notice(warning_str, item['notify_user'], conf)
        log = {item['host_name']: item_detail}
        logger.info(log)


def main():
    if os.name == 'posix':
        daemonize()
    interval_time = 300
    while True:
        try:
            interval_time, inspect_item, conf = get_cfg()
            inspect(inspect_item, conf)
        except Exception as e:
            logger.error(str(e))
        finally:
            sleep(interval_time)


if __name__ == '__main__':
    main()
