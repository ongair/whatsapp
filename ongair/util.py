import os
import logging

def get_env(key):
  return os.environ.get(key).encode('utf-8')

def setup_logging(phone_number):
  env = get_env('env')  
  logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename="logs/%s.%s.log" %(phone_number, env),
    filemode='w')