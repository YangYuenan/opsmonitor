from app import get_logger, get_config
import math
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import utils
from app.models import CfgNotify, HostInfo, MonitorItem, User, ItemStatus, GlobalCfg
from app.main.forms import CfgNotifyForm, HostInfoForm, MonitorItemForm, UserForm, FixHostInfoForm, FixMonitorItemForm, GlobalCfgForm
from . import main

logger = get_logger(__name__)
cfg = get_config()


# 通用列表查询
def common_list(DynamicModel, view, join=None):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 删除操作
    if action == 'del' and id:
        try:
            DynamicModel.get(DynamicModel.id == id).delete_instance()
            flash('删除成功', 'success')
        except:
            flash('删除失败', 'warning')

    # 查询列表
    if join:
        query = DynamicModel.select(DynamicModel, join).join(join).dicts()
    else:
        query = DynamicModel.select().dicts()
    total_count = query.count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template(view, form=dict, current_user=current_user)


# 通用单模型查询&新增&修改
def common_edit(DynamicModel, form, view, join=None):
    id = request.args.get('id', '')
    if id:
        # 查询
        model = DynamicModel.get(DynamicModel.id == id)
        if join:
            data = DynamicModel.select(DynamicModel, join).join(join).where(DynamicModel.id == id).dicts()
        else:
            data = [utils.obj_to_dict(model)]
        if request.method == 'GET':
            utils.model_to_form(data, form)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, model)
                model.save()
                flash('修改成功', 'success')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = DynamicModel()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功', 'success')
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


# 全局配置处理
def cfg_handle(DynamicModel, form, view):
    data = DynamicModel.select().dicts()
    if request.method == 'GET':
        utils.model_to_form(data, form)
    # 修改
    if request.method == 'POST':
        if form.validate_on_submit():
            if data:
                model = DynamicModel.get(DynamicModel.id == data[0]['id'])
            else:
                model = DynamicModel()
            utils.form_to_model(form, model)
            model.save()
            flash('配置成功', 'success')
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


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
