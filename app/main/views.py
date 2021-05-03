from app import get_logger, get_config
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import CfgNotify, HostInfo, MonitorItem, User, GlobalCfg
from app.main.forms import CfgNotifyForm, HostInfoForm, MonitorItemForm, UserForm, FixHostInfoForm, FixMonitorItemForm, GlobalCfgForm
from . import main
from app.main.controller import common_list, common_edit, cfg_handle

logger = get_logger(__name__)
cfg = get_config()


# 根目录跳转
@main.route('/', methods=['GET'])
@login_required
def root():
    return redirect(url_for('main.index'))


# 首页
@main.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html', current_user=current_user)


# 通知方式查询
@main.route('/notifylist', methods=['GET', 'POST'])
@login_required
def notify_list():
    return common_list(CfgNotify, 'notifylist.html')


# 通知方式配置
@main.route('/notifyedit', methods=['GET', 'POST'])
@login_required
def notify_edit():
    return common_edit(CfgNotify, CfgNotifyForm(), 'notifyedit.html')


# 添加主机
@main.route('/addhost', methods=['GET', 'POST'])
@login_required
def add_host():
    return common_edit(HostInfo, HostInfoForm(), 'addhost.html')


# 修改主机信息
@main.route('/fixhost', methods=['GET', 'POST'])
@login_required
def fix_host():
    return common_edit(HostInfo, FixHostInfoForm(), 'addhost.html')


# 编辑主机
@main.route('/edithost', methods=['GET', 'POST'])
@login_required
def edit_host():
    return common_list(HostInfo, 'edithost.html')


# 添加监控
@main.route('/addmonitor', methods=['GET', 'POST'])
@login_required
def add_monitor():
    return common_edit(MonitorItem, MonitorItemForm(), 'addmonitor.html')


# 状态查询
@main.route('/querystatus', methods=['GET', 'POST'])
@login_required
def query_status():
    return common_list(MonitorItem, 'querystatus.html', HostInfo)


# 修改监控
@main.route('/fixmonitor', methods=['GET', 'POST'])
@login_required
def fix_monitor():
    return common_edit(MonitorItem, FixMonitorItemForm(), 'editmonitor.html', HostInfo)


# 用户管理
@main.route('/usermanagement', methods=['GET', 'POST'])
@login_required
def user_management():
    return common_list(User, 'usermanagement.html')


# 编辑用户
@main.route('/edituser', methods=['GET', 'POST'])
@login_required
def edit_user():
    return common_edit(User, UserForm(), 'edituser.html')


# smtp服务器配置
@main.route('/globalcfg', methods=['GET', 'POST'])
@login_required
def global_cfg():
    return cfg_handle(GlobalCfg, GlobalCfgForm(), 'globalcfg.html')
