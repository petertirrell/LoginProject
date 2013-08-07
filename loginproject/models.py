from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Table
    )

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import String
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )
from sqlalchemy.sql import func


from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    unauthenticated_userid
    )

import datetime

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
LogSession = scoped_session(sessionmaker())

Base = declarative_base()


class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, Authenticated, 'edit') ,
                (Allow, 'basic', ('view', 'edit', 'basic')),
                (Allow, 'administrator', ('view', 'edit', 'basic', 'admin'))]
    def __init__(self, request):
        pass


def groupfinder(userid, request):
    # if userid in USERS:
    #     return GROUPS.get(userid, [])
    user = DBSession.query(User).filter(User.id == userid).first()
    return [g.groupname for g in user.groups]


# logging, per http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/logging/sqlalchemy_logger.html
class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True) # auto incrementing
    logger = Column(String(1000)) # the name of the logger. (e.g. myapp.views)
    level = Column(String(255)) # info, debug, or error?
    trace = Column(Text) # the full traceback printout
    msg = Column(Text) # any custom log you may have included
    created_at = Column(DateTime, default=func.now()) # the current timestamp

    def __init__(self, logger=None, level=None, trace=None, msg=None):
        self.logger = logger
        self.level = level
        self.trace = trace
        self.msg = msg

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Log: %s - %s>" % (self.created_at.strftime('%m/%d/%Y-%H:%M:%S'), self.msg[:50])

relat_usergroups = Table('usergroups', Base.metadata,
    Column('userid', Integer, ForeignKey('users.id')),
    Column('groupid', Integer, ForeignKey('groups.id')),
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    providerid = Column(String(255))
    provider = Column(String(255))
    credentials = Column(Text)
    created = Column(DateTime, default=func.now())
    last_login = Column(DateTime)

    profile = relationship("UserProfile", uselist=False, backref="users")
    groups = relationship("Group", secondary=relat_usergroups)

    def __init__(self, providerid, provider, credentials):
        self.providerid = providerid
        self.provider = provider
        self.credentials = credentials


def get_user(request):
    # from http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/auth/user_object.html
    # creates a request.user object that is available

    userid = unauthenticated_userid(request)
    print 'userid {0}'.format(userid)
    if userid is not None:
        # this should return None if the user doesn't exist
        # in the database
        return DBSession.query(User).filter(User.id == userid).first()
    return None


class UserProfile(Base):
    __tablename__ = 'userprofiles'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.id'))    
    displayname = Column(Text)

    def __init__(self, userid):
        self.userid = userid


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    groupname = Column(String(255), unique=True)
    groupdisplayname = Column(String(255))
    groupdesc = Column(Text)

    def __init__(self, groupname):
        self.groupname = groupname
        self.groupdisplayname = groupname


class UserGroup(Base):
    __tablename__ = 'usergroups'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.id'), primary_key=True)
    groupid = Column(Integer, ForeignKey('groups.id'), primary_key=True)      

    def __init__(self, userid, groupid):
        self.userid = userid
        self.groupid = groupid
