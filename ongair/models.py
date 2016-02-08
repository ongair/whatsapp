from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, desc, Float, Text

Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    whatsapp_password = Column(String(255))
    phone_number = Column(String(255))
    setup = Column(Boolean())
    name = Column(String(255))


class Job(Base):
    __tablename__ = 'job_logs'
    id = Column(Integer, primary_key=True)

    method = Column(String(255))
    targets = Column(String())
    args = Column(String())
    sent = Column(Boolean())
    whatsapp_message_id = Column(String(255))
    received = Column(String(Boolean()))
    receipt_timestamp = Column(DateTime())
    message_id = Column(Integer)
    account_id = Column(Integer)
    runs = Column(Integer)
    asset_id = Column(Integer)
    pending = Column(Boolean())
    state = Column(String())


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    receipt_timestamp = Column(DateTime())
    received = Column(Boolean())
    account_id = Column(Integer())
    text = Column(String())
    message_type = Column(String())
    asset_id = Column(Integer())


class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    file_content_type = Column(String())
    file_file_name = Column(String())
    name = Column(String())
    url = Column(String())

    def get_image_file_name(self):
        name = self.name
        if self.file_content_type.encode('utf8').endswith('image/jpeg') or self.file_file_name.encode('utf8').endswith(
                '.jpg'):
            name = "%s.jpg" % name
        elif self.file_content_type.encode('utf8').endswith('image/png') or self.file_file_name.encode('utf8').endswith(
                '.png'):
            name = "%s.png" % name

        return name
