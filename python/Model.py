import sqlalchemy
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

import Config

# Database

Base = declarative_base()

class Student(Base):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True)
    mail = Column(String, index=True)
    password = Column(String)


def init():
    db_engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
                drivername='postgresql+psycopg2',
                database=Config.DB_NAME,
                host=Config.DB_HOST,
                username=Config.DB_USER,
                password=Config.DB_PASSWD))

    Base.metadata.create_all(db_engine)

    s = Student(mail=10)
    print(s.__table__.insert())

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

