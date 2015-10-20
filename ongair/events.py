from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_presence.protocolentities.presence_available import AvailablePresenceProtocolEntity
from util import get_env
from pubnub import Pubnub
import logging, requests, json

logger = logging.getLogger(__name__)

class EventLayer(YowInterfaceLayer):

  @ProtocolEntityCallback("success")
  def onSuccess(self, entity):
    self.connected = True
    self.phone_number = self.getProp('ongair.account')
    self._post('status', { 'status': 1, 'message' : 'Connected' })
    self.init()

    entity = AvailablePresenceProtocolEntity()
    self.toLower(entity)


  @ProtocolEntityCallback("message")
  def onMessage(self, messageProtocolEntity):    
    # send receipts lower
    self.toLower(messageProtocolEntity.ack())

    # sends the read message
    # self.toLower(messageProtocolEntity.ack(True))  

    if not messageProtocolEntity.isGroupMessage():
      if messageProtocolEntity.getType() == 'text':
        self.onTextMessage(messageProtocolEntity)
      elif messageProtocolEntity.getMediaType() == "image" or messageProtocolEntity.getMediaType() == "video":
        self.onMediaMessage(messageProtocolEntity)
    
  @ProtocolEntityCallback("receipt")
  def onReceipt(self, entity):
    self.toLower(entity.ack())

  def onMediaMessage(self, entity):
    by = entity.getFrom(False)
    id = entity.getId()
    name = entity.getNotify()
    
    data = { 'message' : { 'url': entity.url, 'message_type': entity.getMediaType().capitalize(), 'phone_number': by, 'whatsapp_message_id': id, 'name': name }}
    self._post('upload', data)

  def onTextMessage(self, entity):
    text = entity.getBody()
    by = entity.getFrom(False)
    id = entity.getId()
    name = entity.getNotify()

    data = { "message" : { "text" : text, "phone_number" : by, "message_type" : "Text", "whatsapp_message_id" : id, "name" : name  }}
    self._post('messages', data)

    self._sendRealtime({
      'type' : 'text',
      'phone_number' : by,
      'text' : text,
      'name' : name
    })

  def init(self):
    logger.info('Ready to listen to events for %s' %self.phone_number)
    self._initRealtime()

  def _post(self, url, payload):
    post_url = get_env('url') + url
    payload.update(account = self.phone_number)
    headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json' }
    response = requests.post(post_url, data=json.dumps(payload), headers=headers)

  def _sendRealtime(self, message):    
    self.pubnub.publish(channel=self.channel, message=message)

  def _initRealtime(self):
    self.channel = "%s_%s" %(get_env('channel'), self.phone_number)
    self.use_realtime = True
    self.pubnub = Pubnub(get_env('pub_key'), get_env('sub_key'), None, False)