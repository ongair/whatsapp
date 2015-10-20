from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
import logging
logger = logging.getLogger(__name__)

class EventLayer(YowInterfaceLayer):

  EVENTS_CREDENTIALS="ongair.events.credentials"

  @ProtocolEntityCallback("message")
  def onMessage(self, messageProtocolEntity):
    # send receipts lower
    self.toLower(messageProtocolEntity.ack())
    self.toLower(messageProtocolEntity.ack(True))  

  @ProtocolEntityCallback("receipt")
  def onReceipt(self, entity):
    self.toLower(entity.ack())

  def onEvent(self, event):
    if event.getName() == EventLayer.EVENTS_CREDENTIALS:
      self.phone_number = event.getArg('account')
      self.init()


  def init(self):
    logger.info('Ready to listen to events for %s' %self.phone_number)