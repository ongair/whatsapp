#!/usr/bin/python

from layer import VideoUploadLayer
from yowsup.layers.auth                        import YowAuthenticationProtocolLayer
from yowsup.layers.protocol_messages           import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts           import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks               import YowAckProtocolLayer
from yowsup.layers.network                     import YowNetworkLayer
from yowsup.layers.coder                       import YowCoderLayer
from yowsup.layers.protocol_media              import YowMediaProtocolLayer
from yowsup.stacks import YowStack
from yowsup.common import YowConstants
from yowsup.layers import YowLayerEvent
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS
from yowsup import env
from dotenv import load_dotenv
import logging
import sys, getopt, os
from uploader import email

logging.basicConfig(level=logging.DEBUG)

def run(configfile):
  load_dotenv(configfile)
  phone_number = os.environ.get('phone').encode('utf-8')
  password = os.environ.get('password').encode('utf-8')

  CREDENTIALS = (phone_number, password)

  layers = (
    VideoUploadLayer,
    (YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowMediaProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer)
  ) + YOWSUP_CORE_LAYERS

  stack = YowStack(layers)
  stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, CREDENTIALS)         #setting credentials
  stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])    #whatsapp server address
  stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)              
  stack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())          #info about us as WhatsApp client

  stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))   #sending the connect signal

  stack.loop() #this is the program mainloop
  
def main(argv):
  configfile = ''
 
  try:
    opts, args = getopt.getopt(argv,"hc:")
  except getopt.GetoptError:
    print 'run.py -c <configfile>'
    sys.exit(2)
 
  for opt, arg in opts:
    if opt == '-h':
      print 'run.py -c <configfile>'
      sys.exit()
    elif opt in ("-c"):
      configfile = arg
      run(configfile)

if __name__ == "__main__":
  main(sys.argv[1:])