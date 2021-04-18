# -*- coding: utf-8 -*-

import os
import sys
import json
import base64
from datetime import datetime
from peewee import MySQLDatabase, Model, CharField, BooleanField, IntegerField, SmallIntegerField, DateTimeField, \
    ForeignKeyField
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from playhouse.pool import PooledMySQLDatabase

root_path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(root_path)
from app import login_manager
from conf.config import config

cfg = config[os.getenv('FLASK_CONFIG') or 'default']

# db = MySQLDatabase(host=cfg.DB_HOST, port=cfg.DB_PORT, user=cfg.DB_USER, passwd=cfg.DB_PASSWD, database=cfg.DB_DATABASE)
db = PooledMySQLDatabase(
    cfg.DB_DATABASE,
    max_connections=cfg.DB_MAX_CONNECTIONS,
    stale_timeout=cfg.DB_STALE_TIMEOUT,
    user=cfg.DB_USER,
    password=cfg.DB_PASSWD,
    host=cfg.DB_HOST,
    port=cfg.DB_PORT
)


class BaseModel(Model):
    class Meta:
        database = db

    def __str__(self):
        r = {}
        for k in self.__data__.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        # return str(r)
        return json.dumps(r, ensure_ascii=False)


# 管理员工号
class User(UserMixin, BaseModel):
    username = CharField()  # 用户名
    password_hash = CharField()  # 密码
    fullname = CharField()  # 真实性名
    email = CharField()  # 邮箱
    phone = CharField()  # 电话
    status = BooleanField(default=True)  # 生效失效标识

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def verify_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


# 通知人配置
class CfgNotify(BaseModel):
    notify_type = CharField()  # 通知类型：MAIL/SMS
    notify_name = CharField()  # 通知人姓名
    notify_number = CharField()  # 通知号码
    status = BooleanField(default=True)  # 生效失效标识


# 主机信息
class HostInfo(BaseModel):
    host_name = CharField()  # 主机名
    host_ip = CharField()  # 主机ip地址
    host_port = SmallIntegerField(default=22)  # 主机ssh端口
    host_user = CharField()  # 主机连接用户
    host_password_base64 = CharField()  # 主机连接用户的密码

    @property
    def host_password(self):
        return base64.b64decode(self.host_password_base64.encode('utf-8'))

    @host_password.setter
    def host_password(self, raw_password):
        self.host_password_base64 = base64.b64encode(raw_password.encode('utf-8'))


# 监控项
class MonitorItem(BaseModel):
    host = ForeignKeyField(HostInfo, related_name='host_id')  # 监控项对应的主机id，用于查询主机名和主机ip
    item_name = CharField()  # 监控项目名称
    item_type = CharField()  # 监控项目类型（硬盘、cpu、内存、网络、http服务、tcp服务）
    warning_value = SmallIntegerField(default=0)  # 监控项的报警阈值（tcp服务此项为0）
    tcp_http = CharField(default=0)  # tcp服务端口或http服务检查地址（除tcp和http服务外此项为0）
    matching_char = CharField(default=0)  # http服务需要比对返回的字符串，以验证服务的可用性（除http服务外的其他监控项，此项值为0）
    check_time = DateTimeField()  # 监控项更改信息时间
    item_detail = CharField()  # 监控项的检查结果
    item_status = BooleanField(default=True)  # 监控项最新状态（默认正常）
    status = BooleanField(default=True)  # 是否启用监控项


# 监控项状态


class ItemStatus(BaseModel):
    host_name = CharField()  # 监控项对应的主机名
    host_ip = CharField()  # 监控项对应的主机ip
    item_id = IntegerField()  # 监控项id
    item_name = CharField()  # 监控项目名称
    check_time = DateTimeField(default=datetime.now)  # 本条记录的检查时间
    item_detail = CharField()  # 监控项的检查结果
    warning_status = BooleanField(default=False)  # 报警标识（默认不报警）

    class Meta:
        indexes = (
            (('id', 'item_id', 'item_name', 'item_detail', 'check_time'), False),
        )


# 全局配置
class GlobalCfg(BaseModel):
    smtp_server = CharField()  # smtp服务器地址
    smtp_port = SmallIntegerField(default=25)  # smtp服务器端口
    smtp_user = CharField()  # smtp登录用户
    smtp_password_base64 = CharField()  # smtp用户密码
    inspect_interval = IntegerField()  # 检查时间间隔

    @property
    def smtp_password(self):
        return base64.b64decode(self.smtp_password_base64.encode('utf-8'))

    @smtp_password.setter
    def smtp_password(self, raw_password):
        self.smtp_password_base64 = base64.b64encode(raw_password.encode('utf-8'))


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == int(user_id))


# 建表
def create_table():
    db.connect()
    db.create_tables([CfgNotify, User, HostInfo, MonitorItem, ItemStatus, GlobalCfg])


if __name__ == '__main__':
    create_table()
