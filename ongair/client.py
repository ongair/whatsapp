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
from exception import PingTimeoutError, RequestedDisconnectError
from ongair import OngairLayer
import sys
import rollbar
import logging
import pyuploadcare

class Client:
    def __init__(self, phone_number):
        self.connected = False
        self.phone_number = phone_number

        setup_logging(phone_number)

        self.logger = logging.getLogger(__name__)

        environment = get_env('env')
        rollbar_key = get_env('rollbar_key')

        self.yowsup_env = get_env('yowsup_env', False, 's40')

        # initialize rollbar for exception reporting
        rollbar.init(rollbar_key, environment)

        pyuploadcare.conf.pub_key = get_env('uploadcare_public')
        pyuploadcare.conf.secret = get_env('uploadcare_secret')

    def loop(self):
        # set the yowsup environment - not supported in fork
        # YowsupEnv.setEnv(self.yowsup_env)

        stackBuilder = YowStackBuilder()
        # Create the default stack (a pile of layers) and add the Ongair Layer to the top of the stack
        stack = stackBuilder.pushDefaultLayers(True).push(OngairLayer).build()

        ping_interval = int(get_env('ping_interval'))            

        # Set the phone number as a property that can be read by other layers
        stack.setProp(YowIqProtocolLayer.PROP_PING_INTERVAL, ping_interval)
        stack.setProp('ongair.account', self.phone_number)
        stack.setProp(YowNetworkLayer.PROP_ENDPOINT, YowConstants.ENDPOINTS[0])  # whatsapp server address
        stack.setProp(YowCoderLayer.PROP_DOMAIN, YowConstants.DOMAIN)

        # Broadcast the login event. This gets handled by the OngairLayer
        stack.broadcastEvent(YowLayerEvent(OngairLayer.EVENT_LOGIN))        

        try:
            # Run the asyncore loop
            stack.loop(timeout=0.5, discrete=0.5)  # this is the program mainloop
        except AttributeError:
            # for now this is a proxy for ProtocolException i.e. where yowsup has tried to read an 
            # attribute that does not exist
            self.logger.exception("Attribute error")
            rollbar.report_exc_info()
            sys.exit(0)
        except AssertionError:
            # this is a proxy for a wrong expected attribute 
            self.logger.exception("Assertion error")
            rollbar.report_exc_info()
            sys.exit(0)
        except KeyboardInterrupt:
            # manually stopped. more a development debugging issue
            self.logger.info("Manually interupted")
            sys.exit(2)
        except PingTimeoutError:
            self.logger.info("Ping timeout error")
            sys.exit(2)
        except RequestedDisconnectError:
            self.logger.info("We requested to disconnect")
            sys.exit(2)
        except:
            self.logger.exception("Unknown error")
            rollbar.report_exc_info()
            # do not restart as we are not sure what the problem is
            sys.exit(0)
