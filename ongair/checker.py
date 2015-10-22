from dotenv import load_dotenv
from util import get_env
from models import Account, Job, Message
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import sys, getopt, os, argparse, commands


def main(argv):
  parser = argparse.ArgumentParser(description='Description of your program')
  parser.add_argument('-c','--config', help='Path of the config file', required=True)
  
  args = vars(parser.parse_args())
  load_dotenv(args['config'])  

  url = get_env('db')
  db = create_engine(url, echo=False, pool_size=1, pool_timeout=600,pool_recycle=600)
  session = sessionmaker(bind=db)
  sess = session()

  accounts = sess.query(Account).filter_by(setup= True).all()
  for acc in accounts:
    output = commands.getoutput("service ongair-%s status" %acc.phone_number)

    if "stop/waiting" in output:
      print "Account %s-%s needs to start" %(acc.phone_number, acc.name)