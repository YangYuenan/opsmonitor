import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret'
    DB_HOST = '127.0.0.1'
    DB_PORT = 33306
    DB_USER = 'opsmonitor'
    DB_PASSWD = 'opsmonitor'
    DB_DATABASE = 'opsmonitor'
    DB_MAX_CONNECTIONS = 5
    DB_STALE_TIMEOUT = 300
    ITEMS_PER_PAGE = 10
    JWT_AUTH_URL_RULE = '/api/auth'

    SSH_CMD_7 = """
    top -bi -n1|grep Cpu|awk -F',' '{print $4}'|awk '{print 100-$1}';free -m|grep Mem|awk '{print ($3+$6)/$2*100}';df -h |grep -v Use|grep -v tmpfs|awk '{print $5" "$6}'|sort -n|tail -n1;ifconfig eth0|grep bytes|awk '{print $5/1024}'
    """
    SSH_CMD_6 = """
    top -bi -n1|grep Cpu|awk -F',' '{print $4}'|awk '{print 100-$1}';free -m|grep Mem|awk '{print ($3+$6)/$2*100}';df -h |grep -v Use|grep -v tmpfs|awk '{print $5" "$6}'|sort -n|tail -n1;ifconfig eth0|grep bytes|awk '{print $2$6}' |awk -F'bytes:' '{print $2/1024"\n"$3/1024}'
    """

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    PRODUCTION = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
