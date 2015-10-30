
from dotenv import load_dotenv
from util import get_env
from models import Account, Job, Message
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import sys, getopt, os, argparse, commands

def main(argv):
  parser = argparse.ArgumentParser(description='Description of your program')
  parser.add_argument('-c','--config', help='Path of the config file', required=True)
  parser.add_argument('-m','--mode', help='Mode [check,start,activate]', required=True)
  parser.add_argument('-a','--account', help='The phone number we want to activate', required=False)

  args = vars(parser.parse_args())
  load_dotenv(args['config'])

  url = get_env('db')
  db = create_engine(url, echo=False, pool_size=1, pool_timeout=600,pool_recycle=600)
  session = sessionmaker(bind=db)
  sess = session()

  if args['mode'] == "check":
    accounts = sess.query(Account).filter_by(setup= True).all()
    print("Accounts : %s" % len(accounts))
    for acc in accounts:
      output = commands.getoutput("service ongair-%s status" %acc.phone_number)

      if "stop/waiting" in output:
        print "Account %s-%s needs to start" %(acc.phone_number, acc.name)
  elif args['mode'] == "stop":
    accounts = sess.query(Account).filter_by(setup= True).all()
    print("Accounts : %s" % len(accounts))
    for acc in accounts:
      output = commands.getoutput("service ongair-%s status" %acc.phone_number)

      if "start/running" in output:
        output = commands.getoutput("sudo service ongair-%s stop" %acc.phone_number)
        print "Output: %s" %output
  elif args['mode'] == "start":
    accounts = sess.query(Account).filter_by(setup= True).all()
    print("Accounts : %s" % len(accounts))
    for acc in accounts:
      output = commands.getoutput("/sbin/initctl status ongair-%s" %acc.phone_number)

      if "stop/waiting" in output:
        output = commands.getoutput("sudo /sbin/initctl start start ongair-%s" %acc.phone_number)
        print "Output: %s" %output
  elif args['mode'] == "activate":
    str = """
description "Running Ongair via Python"

env PYTHON_HOME=<pwd>/env

start on runlevel [2345]
stop on runlevel [!2345]
normal exit 0 1

exec $PYTHON_HOME/bin/python -W 'ignore:Unverified HTTPS request' <pwd>/ongair/run.py -c <pwd>/.env -a <acc>

respawn
    """
    account = args['account']
    pwd = get_env('pwd')
    str = str.replace('<acc>', account)
    str = str.replace('<pwd>', pwd)

    service_file = open("%songair-%s.conf" %(get_env('service_dir'), account), "w")
    service_file.write(str)
    service_file.close()


if __name__ == "__main__":
  main(sys.argv[1:])

