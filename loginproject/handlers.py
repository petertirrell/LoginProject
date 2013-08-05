import logging
import traceback

import transaction

from models import Log, LogSession

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    synonym
    )

class SQLAlchemyHandler(logging.Handler):
    # A very basic logger that commits a LogRecord to the SQL Db
    def emit(self, record):

        trace = None
        exc = record.__dict__['exc_info']
        if exc:
            trace = traceback.format_exc(exc)

        MyLog = LogSession()  #SessionFactory()
        try:
            log = Log(
                logger=record.__dict__['name'],
                level=record.__dict__['levelname'],
                trace=trace,
                msg=record.__dict__['msg'],)
            MyLog.add(log)
            MyLog.flush()
            MyLog.commit()
            #transaction.commit()
        except Exception as e:
            raise e
        finally:
            MyLog.close()        