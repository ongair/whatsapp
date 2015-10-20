import sys, getopt, os, argparse
from dotenv import load_dotenv
from util import get_env
from client import Client

def run(account):
  client = Client(account)
  client.loop()

def main(argv):
  parser = argparse.ArgumentParser(description='Description of your program')
  parser.add_argument('-c','--config', help='Path of the config file', required=True)
  parser.add_argument('-a','--account', help='Account to start', required=True)
  args = vars(parser.parse_args())


  load_dotenv(args['config'])  
  run(args['account'])

if __name__ == "__main__":
  main(sys.argv[1:])