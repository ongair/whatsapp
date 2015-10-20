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
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS
from yowsup import env
from models import Account
from events import EventLayer

import logging

class Client:
  def __init__(self, phone_number):
    self.connected = False
    self.phone_number = phone_number

    setup_logging(phone_number)
    # self.logger = setup_logging(phone_number)
    self.init_db()
    self.get_account()
    self.logger = logging.getLogger(__name__)

    self.logger.debug('Account is %s' %self.account.name)

  def loop(self):
    layers = (
      EventLayer,
      (YowAuthenticationProtocolLayer, YowMessagesProtocolLayer, YowMediaProtocolLayer, YowReceiptProtocolLayer, YowAckProtocolLayer)
    ) + YOWSUP_CORE_LAYERS

    stackBuilder = YowStackBuilder()
    stack = stackBuilder.pushDefaultLayers(False).push(EventLayer).build()

    stack.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (self.phone_number, self.account.whatsapp_password))         #setting credentials
    stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])    #whatsapp server address
    stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)              
    stack.setProp(YowCoderLayer.PROP_RESOURCE, env.CURRENT_ENV.getResource())          #info about us as WhatsApp client

    stack.broadcastEvent(YowLayerEvent(EventLayer.EVENTS_CREDENTIALS, account=self.phone_number))
    stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))   #sending the connect signal
    
    stack.loop() #this is the program mainloop

  def init_db(self):
    url = get_env('db')
    self.db = create_engine(url, echo=False, pool_size=5, pool_timeout=600,pool_recycle=600)
    self.session = sessionmaker(bind=self.db)

  def get_account(self):
    sess = self.session()
    self.account = sess.query(Account).filter_by(phone_number= self.phone_number).scalar()
    sess.commit()