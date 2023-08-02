from .celery import app as celery_app
import pymysql
__all__ = ('celery_app',)


pymysql.version_info = (1, 4, 3, "final", 0)
pymysql.install_as_MySQLdb()