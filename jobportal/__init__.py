# Make Django's "django.db.backends.mysql" engine work with the pure-python
# PyMySQL driver (no native libmysqlclient build required — important for
# Vercel's serverless Python build environment).
import pymysql

pymysql.install_as_MySQLdb()
# PyMySQL reports a fake MySQLdb version of 1.4.6 for backwards-compatibility
# reasons. Modern Django (>=4.1) requires mysqlclient/MySQLdb >= 2.2.1, so we
# override the reported version here to satisfy that check.
pymysql.version_info = (2, 2, 4, "final", 0)
