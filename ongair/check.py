import sys, getopt, os, argparse
from dotenv import load_dotenv
from util import get_env
from models import Account, Job, Message
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

def run(account):
  url = get_env('db')
  db = create_engine(url, echo=False, pool_size=1, pool_timeout=600,pool_recycle=600)
  session = sessionmaker(bind=db)
  sess = session()
  account = sess.query(Account).filter_by(phone_number= account).scalar()
  sess.commit()

  print 'Account: %s' %account.phone_number
  print 'Password: %s' %account.whatsapp_password

def main(argv):
  parser = argparse.ArgumentParser(description='Description of your program')
  parser.add_argument('-c','--config', help='Path of the config file', required=True)
  parser.add_argument('-a','--account', help='Account to start', required=True)
  args = vars(parser.parse_args())


  load_dotenv(args['config'])  
  run(args['account'])

if __name__ == "__main__":
  main(sys.argv[1:])