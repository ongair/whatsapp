from util import setup_logging, get_env
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.protocol_messages import YowMessagesProtocolLayer
from yowsup.layers.protocol_receipts import YowReceiptProtocolLayer
from yowsup.layers.protocol_acks import YowAckProtocolLayer
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.coder import YowCoderLayer
from yowsup.layers.protocol_media import YowMediaProtocolLayer
from yowsup.layers.protocol_iq import YowIqProtocolLayer
from yowsup.stacks import YowStack
from yowsup.stacks import YowStackBuilder
from yowsup.common import YowConstants
from yowsup.layers import YowLayerEvent
from yowsup.layers import YowParallelLayer
from yowsup.stacks import YowStack, YOWSUP_CORE_LAYERS
from yowsup.env import YowsupEnv
from ongair import OngairLayer
from stack import OngairStackBuilder
import sys
import rollbar


class Client:
    def __init__(self, phone_number, encrypted=True):
        self.connected = False
        self.encrypted = encrypted
        self.phone_number = phone_number

        setup_logging(phone_number)

        environment = get_env('env')
        rollbar_key = get_env('rollbar_key')

        # initialize rollbar for exception reporting
        rollbar.init(rollbar_key, environment)

    def loop(self):
        stackBuilder = YowStackBuilder()
        # Create the default stack (a pile of layers) and add the Ongair Layer to the top of the stack
        stack = stackBuilder.pushDefaultLayers(True).push(OngairLayer).build()

        ping_interval = int(get_env('ping_interval'))            

        # Set the phone number as a property that can be read by other layers
        stack.setProp(YowIqProtocolLayer.PROP_PING_INTERVAL, ping_interval)
        stack.setProp('ongair.account', self.phone_number)
        stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])  # whatsapp server address
        stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)
        
        # YowsupEnv.setEnv('android')
        YowsupEnv.setEnv('s40')

        # Broadcast the login event. This gets handled by the OngairLayer
        stack.broadcastEvent(YowLayerEvent(OngairLayer.EVENT_LOGIN))        

        try:
            # Run the asyncore loop
            stack.loop(timeout=5, discrete=0.5)  # this is the program mainloop
        except AttributeError:
            # for now this is a proxy for ProtocolException i.e. where yowsup has tried to read an 
            # attribute that does not exist
            rollbar.report_exc_info()
            sys.exit(2)