from util import setup_logging, get_env
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yowsup.layers.auth                        import YowAuthenticationProtocolLayer
from yowsup.layers.protocol_messages           import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts           import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks               import YowAckProtocolLayer
from yowsup.layers.network                     import YowNetworkLayer
from yowsup.layers.coder                       import YowCoderLayer
from yowsup.layers.protocol_media              import YowMediaProtocolLayer
from yowsup.stacks import YowStack
from yowsup.stacks import YowStackBuilder
from yowsup.common import YowConstants
from yowsup.layers import YowLayerEvent
from yowsup.layers import YowParallelLayer
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS
from yowsup import env
from ongair import OngairLayer

class Client:  

  def __init__(self, phone_number):
    self.connected = False
    self.phone_number = phone_number

    setup_logging(phone_number)


  def loop(self):
    stackBuilder = YowStackBuilder()
    # stack = stackBuilder.pushDefaultLayers(False).push(JobsLayer).push(EventLayer).build()
    stack = stackBuilder.pushDefaultLayers(False).push(OngairLayer).build()

    stack.setProp('ongair.account', self.phone_number)    
    stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])    #whatsapp server address
    stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)              
    stack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())          #info about us as WhatsApp client
    stack.broadcastEvent(YowLayerEvent(OngairLayer.EVENT_LOGIN))
    stack.loop(timeout = 5, discrete = 0.5) #this is the program mainloop