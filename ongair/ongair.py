from yowsup.layers.protocol_presence.protocolentities.presence_available import AvailablePresenceProtocolEntity
from yowsup.layers.auth                                 import YowAuthenticationProtocolLayer
from yowsup.layers.interface                            import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.network                              import YowNetworkLayer
from yowsup.layers.protocol_messages.protocolentities   import TextMessageProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities   import GetSyncIqProtocolEntity, ResultSyncIqProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities   import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities       import OutgoingAckProtocolEntity
from yowsup.layers.protocol_profiles.protocolentities import SetStatusIqProtocolEntity
from yowsup.layers import YowLayerEvent
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from util import get_env, post_to_server
from models import Account, Job, Message
from datetime import datetime
from pubnub import Pubnub

import logging, requests, json

logger = logging.getLogger(__name__)

class OngairLayer(YowInterfaceLayer):

  EVENT_LOGIN = 'ongair.events.login'

  @ProtocolEntityCallback("success")
  def onSuccess(self, entity):
    self.connected = True
    self.phone_number = self.getProp('ongair.account')
    self._post('status', { 'status': 1, 'message' : 'Connected' })    

    entity = AvailablePresenceProtocolEntity()
    self.toLower(entity)
    self.work()
    self.pingCount = 0

  @ProtocolEntityCallback("message")
  def onMessage(self, messageProtocolEntity):    
    # send receipts lower
    self.toLower(messageProtocolEntity.ack())

    if not messageProtocolEntity.isGroupMessage():
      if messageProtocolEntity.getType() == 'text':
        self.onTextMessage(messageProtocolEntity)
      elif messageProtocolEntity.getMediaType() == "image" or messageProtocolEntity.getMediaType() == "video":
        self.onMediaMessage(messageProtocolEntity)

  @ProtocolEntityCallback("receipt")
  def onReceipt(self, entity):
    ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())    
    self.toLower(ack)

    id = entity.getId()
    receipt_type = entity.getType()

    _session = self.session()
    job = _session.query(Job).filter_by(account_id= self.account.id, whatsapp_message_id=id, method= 'sendMessage').scalar()
    if job is not None:
      message = _session.query(Message).get(job.message_id)
      if message is not None:
          message.received = True
          message.receipt_timestamp = datetime.now()          
          _session.commit()          

          if receipt_type == 'read':
            data = { 'receipt' : { 'type' : 'read', 'message_id': message.id }}
            post_to_server('receipt', self.phone_number, data) 

  @ProtocolEntityCallback("iq")
  def onIq(self, entity):
    logger.info('ProtocolEntityCallback. Count is %s' %self.pingCount)
    self.pingCount += 1
    self.work()

    if self.pingCount % 60 == 0:
      logger.info('Send online signal to app.ongair.im')
      self._post('status', { 'status': '1', 'message' : 'Connected' })    

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

    logger.info("Received message %s from %s" %(text, by))

    data = { "message" : { "text" : text, "phone_number" : by, "message_type" : "Text", "whatsapp_message_id" : id, "name" : name  }}
    self._post('messages', data)

    self._sendRealtime({
      'type' : 'text',
      'phone_number' : by,
      'text' : text,
      'name' : name
    })

  def work(self):
    _session = self.session()
    jobs = _session.query(Job).filter_by(sent=False, account_id=self.account.id, pending=False).all()
    logger.info("Number of jobs ready to run %s" % len(jobs))    

    for job in jobs:
      logger.info('Job %s with args %s and targets %s' %(job.method, job.args, job.targets))
      if job.method == 'sync':
        self.sync(job)
      elif job.method == 'sendMessage':
        self.send(job, _session)
      elif job.method == 'profile_setStatus':
        self.setProfile(job)

    _session.commit()

  def sync(self, job):    
    contacts = job.targets.split(',')
    syncEntity = GetSyncIqProtocolEntity(contacts)
    self._sendIq(syncEntity, self.onGetSyncResult, self.onGetSyncError)
    logger.info('Sent sync request for %s' %contacts)
    job.runs += 1
    job.sent = True

  def send(self, job, session):
    messageEntity = TextMessageProtocolEntity(job.args.encode('utf8'), to = "%s@s.whatsapp.net" % job.targets)
    job.whatsapp_message_id = messageEntity.getId()
    job.sent = True    
    session.commit()
    self.toLower(messageEntity)

  def setProfile(self, job):
    entity = SetStatusIqProtocolEntity(job.args.encode('utf8'))
    self._sendIq(entity, self.onHandleSetProfile, self.onHandleSetProfile)
    job.sent = True

  def onHandleSetProfile(result, original):
    logger.info('Result from setting the profile %s' %result)

  def onGetSyncResult(self, resultSyncIqProtocolEntity, originalIqProtocolEntity):
    post_to_server('contacts/sync', self.phone_number, { 'registered' : resultSyncIqProtocolEntity.outNumbers.keys(), 'unregistered' : resultSyncIqProtocolEntity.invalidNumbers })

  def onGetSyncError(self, errorSyncIqProtocolEntity, originalIqProtocolEntity):
    logger.info(errorSyncIqProtocolEntity)

  def init_db(self):
    url = get_env('db')
    self.db = create_engine(url, echo=False, pool_size=1, pool_timeout=600,pool_recycle=600)
    self.session = sessionmaker(bind=self.db)

  def onEvent(self, event):
    if event.getName() == OngairLayer.EVENT_LOGIN:
      self.phone_number = self.getProp('ongair.account')
      self.init()

  def init(self):
    self.init_db()
    self._initRealtime()
    self.get_account()
    self.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (self.phone_number, self.account.whatsapp_password))
    logger.info('About to login : %s' %self.account.name)
    self.getStack().broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT)) 

  def get_account(self):
    sess = self.session()
    self.account = sess.query(Account).filter_by(phone_number= self.phone_number).scalar()
    sess.commit()

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