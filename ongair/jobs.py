from yowsup.layers.auth                                 import YowAuthenticationProtocolLayer
from yowsup.layers.interface                            import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.network                              import YowNetworkLayer
from yowsup.layers.protocol_messages.protocolentities   import TextMessageProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities   import GetSyncIqProtocolEntity, ResultSyncIqProtocolEntity
from yowsup.layers import YowLayerEvent
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from util import get_env, post_to_server
from models import Account, Job

import logging

logger = logging.getLogger(__name__)
class JobsLayer(YowInterfaceLayer):

  EVENT_LOGIN = 'ongair.events.login'

  @ProtocolEntityCallback("success")
  def onSuccess(self, entity):
    self.init_db()
    self.work()

  @ProtocolEntityCallback("iq")
  def onIq(self, entity):
    logger.info('ProtocolEntityCallback')
    self.work()

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

    _session.commit()

  def sync(self, job):    
    contacts = job.targets.split(',')
    syncEntity = GetSyncIqProtocolEntity(contacts)
    self._sendIq(syncEntity, self.onGetSyncResult, self.onGetSyncError)
    logger.info('Sent sync request for %s' %contacts)
    job.runs += 1
    job.sent = True

  def send(self, job, session):
    messageEntity = TextMessageProtocolEntity(job.args, to = "%s@s.whatsapp.net" % job.targets)
    job.whatsapp_message_id = messageEntity.getId()
    job.sent = True    
    session.commit()
    self.toLower(messageEntity)

  def onGetSyncResult(self, resultSyncIqProtocolEntity, originalIqProtocolEntity):
    post_to_server('contacts/sync', self.phone_number, { 'registered' : resultSyncIqProtocolEntity.outNumbers.keys(), 'unregistered' : resultSyncIqProtocolEntity.invalidNumbers })

  def onGetSyncError(self, errorSyncIqProtocolEntity, originalIqProtocolEntity):
    logger.info(errorSyncIqProtocolEntity)

  def init_db(self):
    url = get_env('db')
    self.db = create_engine(url, echo=False, pool_size=1, pool_timeout=600,pool_recycle=600)
    self.session = sessionmaker(bind=self.db)

  def onEvent(self, event):
    if event.getName() == JobsLayer.EVENT_LOGIN:
      self.phone_number = self.getProp('ongair.account')
      self.init()

  def init(self):
    self.init_db()
    self.get_account()
    self.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS, (self.phone_number, self.account.whatsapp_password))
    logger.info('About to login : %s' %self.account.name)
    self.getStack().broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT)) 

  def get_account(self):
    sess = self.session()
    self.account = sess.query(Account).filter_by(phone_number= self.phone_number).scalar()
    sess.commit()
      