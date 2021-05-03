# -*- coding: utf-8 -*-

__author__ = 'yangyuenan'
__time__ = '2021/5/2 18:27'


import math
from app import utils
from app import get_logger, get_config
from flask import render_template, flash, request
from flask_login import current_user


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
