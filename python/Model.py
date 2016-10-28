import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import Config

# Database

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    mail = Column(String, unique=True)
    password = Column(String)
    power = Column(Integer)

    def __repr__(self):
        return '<User(mail="%s", password="%s", power="%d")>' % (
                                self.mail, self.password, self.power)

class AuthToken(Base):
    __tablename__ = 'authtoken'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("user.id"))
    token = Column(String)


class UserData(Base):
    __tablename__ = 'userdata'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("user.id"))
    full_name = Column(String)
    gender = Column(Integer)
    school = Column(String)
    school_type = Column(Integer)
    grade = Column(Integer)
    address = Column(String)
    phone = Column(String)
    area = Column(Integer)


def init():
    db_engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
                drivername='postgresql+psycopg2',
                database=Config.DB_NAME,
                host=Config.DB_HOST,
                username=Config.DB_USER,
                password=Config.DB_PASSWD))

    Base.metadata.create_all(db_engine)

    #Session = sessionmaker(bind=db_engine)
    #session = Session()
    # u = User(mail='luniacslime@gmail.com', password='1234', power=-1)
    # print(u)
    # session.add(u)
    # session.commit()


# Mail
import smtplib


class SMTPMail(object):
    def __init__(self):
        self.username = Config.SMTP_USER
        self.password = Config.SMTP_PASSWD
    
    def send(self, to, subject, content):
        smtp_server = smtplib.SMTP(Config.SMTP_HOST)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login(self.username, self.password)

        header = ('To:%s\n'
                  'From:%s\n'
                  'Subject:%s\n') % (to, self.username, subject)
        msg = '%s\n %s \n\n' % (header, content)
        smtp_server.sendmail(self.username, to, msg)
        smtp_server.close()

