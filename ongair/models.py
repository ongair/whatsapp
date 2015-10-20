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