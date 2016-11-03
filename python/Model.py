import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import Config


DEBUG = True


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
    __tablename__ = 'auth_token'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    token = Column(String)


class UserData(Base):
    __tablename__ = 'user_data'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    full_name = Column(String)
    gender = Column(Integer)
    school = Column(String)
    school_type = Column(Integer)
    grade = Column(Integer)
    address = Column(String)
    phone = Column(String)


class SetPasswordToken(Base):
    __tablename__ = 'set_password_token'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    token = Column(String)


class Poll(Base):
    __tablename__ = 'poll'

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    body = Column(String)
    order = Column(Integer)
    year = Column(Integer)
    status = Column(Integer)


class Qa(Base):
    __tablename__ = 'qa'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    order = Column(Integer)
    status = Column(Integer)


class GenderOption(Base):
    __tablename__ = 'gender_option'

    id = Column(Integer, primary_key=True)
    value = Column(String)


class SchoolTypeOption(Base):
    __tablename__ = 'school_type_option'

    id = Column(Integer, primary_key=True)
    value = Column(String)
    max_grade = Column(Integer)


def init():
    db_engine = sqlalchemy.create_engine(sqlalchemy.engine.url.URL(
                drivername='postgresql+psycopg2',
                database=Config.DB_NAME,
                host=Config.DB_HOST,
                username=Config.DB_USER,
                password=Config.DB_PASSWD))

    Base.metadata.create_all(db_engine)

    Session = sessionmaker(bind=db_engine)
    session = Session()

    def insertInstance(instance):
        try:
            session.add(instance)
            session.commit()
        except Exception as e:
            session.rollback()

    # Initialize for some constant data
    session.query(GenderOption).delete()
    genders = ['女生', '男生']
    for i in range(len(genders)):
        instance = GenderOption(id=(i + 1), value=genders[i])
        insertInstance(instance)

    session.query(SchoolTypeOption).delete()
    school_types = [('國中', 3), ('高中', 3)]
    for i in range(len(school_types)):
        instance = SchoolTypeOption(id=(i + 1), value=school_types[i][0], max_grade=school_types[i][1])
        insertInstance(instance)


# Mail
import smtplib
from email.mime.text import MIMEText
from email.header import Header

class SMTPMail(object):
    def __init__(self):
        self.username = Config.SMTP_USER
        self.password = Config.SMTP_PASSWD
        self.sender = Config.SMTP_SENDER
    
    def send(self, to, subject, plain_content, html_content):
        smtp_server = smtplib.SMTP(Config.SMTP_HOST)
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.login(self.username, self.password)

        header = MIMEText(plain_content.encode('utf-8'), 'plain', 'utf-8')
        header = MIMEText(html_content.encode('utf-8'), 'html', 'utf-8')
        header['From'] = Header(self.sender, 'utf-8')
        header['To'] = to
        header['Subject'] = Header(subject, 'utf-8')
        smtp_server.sendmail(self.username, to, header.as_string())
        smtp_server.close()

