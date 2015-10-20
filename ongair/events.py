from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from util import get_env
import logging, requests, json

logger = logging.getLogger(__name__)

class EventLayer(YowInterfaceLayer):

  EVENTS_CREDENTIALS="ongair.events.credentials"

  @ProtocolEntityCallback("message")
  def onMessage(self, messageProtocolEntity):    
    # send receipts lower
    self.toLower(messageProtocolEntity.ack())
    # sends the read message
    # self.toLower(messageProtocolEntity.ack(True))  

    logger.info('Received message %s' %messageProtocolEntity.getNotify())

    if not messageProtocolEntity.isGroupMessage():
      if messageProtocolEntity.getType() == 'text':
        self.onTextMessage(messageProtocolEntity)

  @ProtocolEntityCallback("receipt")
  def onReceipt(self, entity):
    self.toLower(entity.ack())

  def onEvent(self, event):
    if event.getName() == EventLayer.EVENTS_CREDENTIALS:
      self.phone_number = event.getArg('account')
      self.init()

  def onTextMessage(self, entity):
    text = entity.getBody()
    by = entity.getFrom(False)
    id = entity.getId()

    data = { "message" : { "text" : text, "phone_number" : by, "message_type" : "Text", "whatsapp_message_id" : id, "name" : entity.getNotify()  }}
    self._post('messages', data)

  def init(self):
    logger.info('Ready to listen to events for %s' %self.phone_number)

  def _post(self, url, payload):
    post_url = get_env('url') + url
    payload.update(account = self.phone_number)
    headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json' }
    response = requests.post(post_url, data=json.dumps(payload), headers=headers)