import sys, getopt, os, argparse
from util import get_env
from client import Client


def run(account):
    client = Client(account, get_env('encrypted'))
    client.loop()


def main(argv):
    parser = argparse.ArgumentParser(description='Description of your program')
    args = vars(parser.parse_args())

    run(args['account'])


if __name__ == "__main__":
    main(sys.argv[1:])
