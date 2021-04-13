from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, DateField, \
    IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, IPAddress, NumberRange, AnyOf, \
    ValidationError
from ..models import db, User, HostInfo, MonitorItem
from peewee import DoesNotExist


class CfgNotifyForm(FlaskForm):
    notify_type = SelectField('通知类型', choices=[('MAIL', '邮件通知'), ('SMS', '短信通知')],
                              validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    notify_name = StringField('通知人姓名', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    notify_number = StringField('通知号码', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    status = BooleanField('生效标识', default=True)
    submit = SubmitField('提交')


# 主机信息表单
class HostInfoForm(FlaskForm):
    host_name = StringField('主机名', validators=[DataRequired(message='不能为空'), Length(0, 16, message='长度不正确')])
    host_ip = StringField('主机ip', validators=[DataRequired(message='不能为空'),
                                              IPAddress(ipv4=True, ipv6=False, message='请输入合法的ip地址')])
    host_port = IntegerField('主机ssh端口', validators=[NumberRange(1, 65535, message='请输入合法的端口号')], default=22)
    host_user = StringField('主机用户', validators=[DataRequired(message='不能为空')], default='root')
    host_password = PasswordField('主机用户密码', validators=[DataRequired(message='不能为空'), Length(4, 16, message='长度不正确')])
    submit = SubmitField('提交')

    def validate_host_name(self, field):
        try:
            if HostInfo.get(HostInfo.host_name == field.data):
                raise ValidationError('该主机名已被注册')
        except DoesNotExist:
            pass

    def validate_host_ip(self, field):
        try:
            if HostInfo.get(HostInfo.host_ip == field.data):
                raise ValidationError('该ip已被注册')
        except DoesNotExist:
            pass


class FixHostInfoForm(FlaskForm):
    host_name = StringField('主机名', validators=[DataRequired(message='不能为空'), Length(0, 16, message='长度不正确')])
    host_ip = StringField('主机ip', validators=[IPAddress(ipv4=True, ipv6=False, message='请输入合法的ip地址')])
    host_port = IntegerField('主机ssh端口', validators=[NumberRange(1, 65535, message='请输入合法的端口号')], default=22)
    host_user = StringField('主机用户', validators=[DataRequired(message='不能为空')], default='root')
    host_password = PasswordField('主机用户密码', validators=[DataRequired(message='不能为空'), Length(4, 16, message='长度不正确')])
    submit = SubmitField('提交')


# 监控项表单
class MonitorItemForm(FlaskForm):
    host = SelectField('主机名称', validators=[DataRequired(message='请选择主机')], coerce=int)
    item_name = StringField('监控项名称', validators=[DataRequired(message='不能为空'), Length(0, 16, message='长度不正确')])
    item_type = SelectField('项目类型',
                            choices=[('cpu', 'cpu'), ('内存', '内存'), ('硬盘', '硬盘'), ('网络', '网络'), ('http服务', 'http服务'),
                                     ('tcp服务', 'tcp服务')],
                            validators=[DataRequired(message='请选择监控项')])
    warning_value = IntegerField('报警阈值(cpu、内存、硬盘为使用率，网络为传输速率 KB/s)', validators=[Length(0, 5, message='长度不正确')], default=0)
    tcp_http = StringField('tcp和http配置(tcp服务填端口号，http服务填连接地址,其余不填)', default=0)
    matching_char = StringField('比对字符串(http服务需填，其余不填)', validators=[Length(0, 255, message='长度不正确')], default=0)
    status = BooleanField('启用标识', default=True)
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(MonitorItemForm, self).__init__(*args, **kwargs)
        self.host.choices = [(host.id, host.host_name) for host in HostInfo.select()]

    def validate(self):
        try:
            if MonitorItem.get(MonitorItem.host == self.host.data,
                               MonitorItem.item_name == self.item_name.data):
                raise ValidationError('已存在该检查项')
        except DoesNotExist:
            return True


# 修改监控项表单
class FixMonitorItemForm(FlaskForm):
    host_name = StringField('主机名称', validators=[DataRequired(message='请选择主机')])
    item_name = StringField('监控项名称', validators=[DataRequired(message='不能为空'), Length(0, 16, message='长度不正确')])
    item_type = StringField('项目类型', validators=[DataRequired(message='请选择监控项')])
    warning_value = IntegerField('报警阈值(cpu、内存、硬盘为使用率，网络为传输速率 KB/s)', validators=[NumberRange(0, 10240, message='请输入0-10000之间的数值')], default=0)
    matching_char = StringField('比对字符串', validators=[Length(0, 255, message='长度不正确')], default=0)
    submit = SubmitField('提交')


# 图表时间选择表单
class ChartForm(FlaskForm):
    date_ware = DateField('日期范围', format='%Y-%m-%d')
    submit = SubmitField('提交')


# 用户表单
class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='不能为空'), Length(0, 8, message='长度不正确')])
    password1 = PasswordField('用户密码', validators=[DataRequired(message='不能为空'), Length(4, 16, message='长度不正确')])
    password2 = PasswordField('再次输入密码', validators=[DataRequired(message='不能为空'),
                                                    Length(4, 16, message='长度不正确'),
                                                    EqualTo('password1', message='两次输入的密码不一致')])
    fullname = StringField('真实姓名', validators=[DataRequired(message='不能为空'), Length(0, 8, message='长度不正确')])
    email = StringField('邮箱', validators=[DataRequired(message='不能为空'), Email(message='邮箱格式不正确')])
    phone = StringField('电话', validators=[DataRequired(message='不能为空'), Length(11, 11, message='电话号码格式不正确')])
    status = BooleanField('生效标识', default=True)
    submit = SubmitField('提交')


# 全局配置表单
class GlobalCfgForm(FlaskForm):
    smtp_server = StringField('SMTP服务器地址', validators=[DataRequired(message='不能为空')])
    smtp_port = IntegerField('SMTP服务端口', validators=[NumberRange(1, 65535, message='请输入合法的端口号')], default=25)
    smtp_user = StringField('SMTP服务登录用户', validators=[DataRequired(message='不能为空')])
    smtp_password = PasswordField('SMTP服务登录密码', validators=[DataRequired(message='不能为空')])
    inspect_interval = IntegerField('检查时间间隔（min）', validators=[DataRequired(message='不能为空'),
                                                               NumberRange(1, 10, message='时间间隔最大为10分钟')])
    submit = SubmitField('提交')
