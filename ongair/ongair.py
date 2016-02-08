from yowsup.layers.protocol_presence.protocolentities.presence_available import AvailablePresenceProtocolEntity
from yowsup.layers.auth import YowAuthenticationProtocolLayer
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities import GetSyncIqProtocolEntity, ResultSyncIqProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import OutgoingAckProtocolEntity
from yowsup.layers.protocol_profiles.protocolentities import SetStatusIqProtocolEntity
from yowsup.layers.protocol_profiles.protocolentities import SetPictureIqProtocolEntity
from yowsup.layers.protocol_media.protocolentities import RequestUploadIqProtocolEntity
from yowsup.layers.protocol_media.protocolentities import ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.layers import YowLayerEvent
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from util import get_env, post_to_server, download, normalizeJid, cleanup_file
from models import Account, Job, Message, Asset
from datetime import datetime
from pubnub import Pubnub
from PIL import Image

import logging, requests, json, sys

logger = logging.getLogger(__name__)


class OngairLayer(YowInterfaceLayer):
    EVENT_LOGIN = 'ongair.events.login'

    @ProtocolEntityCallback("success")
    def onSuccess(self, entity):
        self.connected = True
        self.phone_number = self.getProp('ongair.account')
        self._post('status', {'status': 1, 'message': 'Connected'})

        entity = AvailablePresenceProtocolEntity()
        self.toLower(entity)
        self.work()
        self.pingCount = 0

    @ProtocolEntityCallback("failure")
    def onFailure(self, entity):
        self.connected = False
        logger.info("Login Failed, reason: %s" % entity.getReason())

        # TODO: Where is the notification?
        if entity.getReason() == "not-authorized":
            _session = self.session()
            self.account.setup = False
            _session.commit()

        sys.exit(0)  # does not restart

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
        job = _session.query(Job).filter_by(account_id=self.account.id, whatsapp_message_id=id,
                                            method='sendMessage').scalar()
        if job is not None:
            message = _session.query(Message).get(job.message_id)
            if message is not None:
                # TODO: Make this uniform. Post the received to the API instead of updating the DB
                message.received = True
                message.receipt_timestamp = datetime.now()
                _session.commit()

                if receipt_type == 'read':
                    data = {'receipt': {'type': 'read', 'message_id': message.id}}
                    post_to_server('receipt', self.phone_number, data)

    @ProtocolEntityCallback("iq")
    def onIq(self, entity):
        logger.info('ProtocolEntityCallback. Count is %s' % self.pingCount)
        self.pingCount += 1
        # Whenever we are pinged by whatsapp, poll the database for pending jobs
        self.work()

        if self.pingCount % 10 == 0:
            logger.info('Send online signal to app.ongair.im')
            self._post('status', {'status': '1', 'message': 'Connected'})

    def onMediaMessage(self, entity):
        by = entity.getFrom(False)
        id = entity.getId()
        name = entity.getNotify()
        preview = None

        data = {'message': {'url': entity.url, 'message_type': entity.getMediaType().capitalize(), 'phone_number': by,
                            'whatsapp_message_id': id, 'name': name, 'caption': entity.getCaption()}}
        self._post('upload', data)

    def onTextMessage(self, entity):
        text = entity.getBody()
        by = entity.getFrom(False)
        id = entity.getId()
        name = entity.getNotify()

        logger.info("Received message %s from %s" % (text, by))

        data = {"message": {"text": text, "phone_number": by, "message_type": "Text", "whatsapp_message_id": id,
                            "name": name}}
        self._post('messages', data)

        self._sendRealtime({
            'type': 'text',
            'phone_number': by,
            'text': text,
            'name': name
        })

    def work(self):
        _session = self.session()
        jobs = _session.query(Job).filter_by(sent=False, account_id=self.account.id, pending=False).all()
        logger.info("Number of jobs ready to run %s" % len(jobs))

        for job in jobs:
            logger.info('Job %s with args %s and targets %s' % (job.method, job.args, job.targets))
            if job.method == 'sync':
                self.sync(job)
            elif job.method == 'sendMessage':
                self.send(job, _session)
            elif job.method == 'profile_setStatus':
                self.setProfileStatus(job)
            elif job.method == "setProfilePicture":
                self.setProfilePicture(job)
            elif job.method == 'sendImage':
                self.sendImage(job)

        _session.commit()

    def sync(self, job):
        contacts = job.targets.split(',')
        syncEntity = GetSyncIqProtocolEntity(contacts)
        self._sendIq(syncEntity, self.onGetSyncResult, self.onGetSyncError)
        logger.info('Sent sync request for %s' % contacts)
        job.runs += 1
        job.sent = True

    def send(self, job, session):
        messageEntity = TextMessageProtocolEntity(job.args.encode('utf8'), to="%s@s.whatsapp.net" % job.targets)
        job.whatsapp_message_id = messageEntity.getId()
        job.sent = True
        session.commit()
        self.toLower(messageEntity)

    def setProfileStatus(self, job):
        entity = SetStatusIqProtocolEntity(job.args.encode('utf8'))
        self._sendIq(entity, self.onHandleSetProfileStatus, self.onHandleSetProfileStatus)
        job.sent = True

    def setProfilePicture(self, job):
        url = job.args
        file = download(url)

        src = Image.open(file)
        pictureData = src.resize((640, 640)).tobytes("jpeg", "RGB")
        picturePreview = src.resize((96, 96)).tobytes("jpeg", "RGB")
        iq = SetPictureIqProtocolEntity(self.getOwnJid(), picturePreview, pictureData)
        self._sendIq(iq, self.onHandleSetProfilePicture, self.onHandleSetProfilePicture)
        job.sent = True

    # This function sends an image to a contact
    def sendImage(self, job):
        """ Send an image to a contact.

        """

        # create db session
        _session = self.session()

        # get the message
        message = _session.query(Message).get(job.message_id)
        caption = message.text

        logger.debug('Retrieved the message with caption %s of type %s' %(caption, message.message_type))

        asset = _session.query(Asset).get(message.asset_id)
        if asset is not None:
            url = asset.url
            file_name = asset.name

            logger.debug('About to download %s from %s' %(file_name, url)) 

            # download the file
            path = download(url, file_name)
            logger.debug('File downloaded to %s' %path)

            # get whatsapp username from targets
            target = normalizeJid(job.targets)

            # create the upload request entity
            entity = RequestUploadIqProtocolEntity(RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, filePath=path)

            # the success callback
            successFn = lambda successEntity, originalEntity: self.onRequestUploadSuccess(target, path, successEntity, originalEntity, caption)

            # The on error callback 
            errorFn = lambda errorEntity, originalEntity: self.onRequestUploadError(target, path, errorEntity, originalEntity)        

            logger.info('About to sent the iq')
            self._sendIq(entity, successFn, errorFn)

            job.sent = True

    # This function actually sends the image to the target via WhatsApp
    def imageSend(self, filePath, url, to, ip=None, caption=None):
        
        # create the entity object to be passed down
        entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(filePath, url, ip, to, caption=caption)
        logger.debug('Sending image %s to %s' %(url, to))

        self.toLower(entity)

    # This function is called when the request to upload an image is successful
    def onRequestUploadSuccess(self, to, path, result, original, caption):
        if result.isDuplicate():
            # This image is already on WhatsApp servers

            logger.info("The image %s is already on the WhatsApp server" %path)
            self.imageSend(path, result.getUrl(), to, result.getIp(), caption)
        else:
            # We need to upload the image to WhatsApp servers

            # The on success callback
            successFn = lambda filePath, jid, url: self.onUploadSuccess(path, url, to,
                                                                        result.getIp(),
                                                                        caption)

            # create the actual uploader
            mediaUploader = MediaUploader(to, self.getOwnJid(), path,
                                          result.getUrl(),
                                          result.getResumeOffset(),
                                          successFn, 
                                          self.onUploadError, #upload error
                                          self.onUploadProgress, #upload progress
                                          async=False)
            # begin the upload
            mediaUploader.start()

    # This function is called when the image upload to WhatsApp servers was successful
    def onUploadSuccess(self, filePath, url, to, ip, caption):

        # call the actual image send
        self.imageSend(filePath, url, to, ip, caption)

    # This function is called when there is an upload error
    def onUploadError(self, filePath, jid, url):

        #TODO: add the job id so we can track errors and retry
        logger.info("Upload file %s to %s for %s failed!" % (filePath, url, jid))

    # This function is called by the uploader to report progress - not essential
    def onUploadProgress(self, filePath, jid, url, progress):
        logger.debug("Uploading file %s progress is %s" %(url, progress))
        return None

    # This function is called when there is an error with requesting an upload
    def onRequestUploadError(self, jid, path, result, original):

        #TODO: add the job id so we can track errors and retry
        logger.info('Error with uploading image %s' % path)

    def onHandleSetProfilePicture(self, result, original):
        logger.info('Result from setting the profile picture %s' % result)

    def onHandleSetProfileStatus(self, result, original):
        logger.info('Result from setting the profile %s' % result)

    def onGetSyncResult(self, resultSyncIqProtocolEntity, originalIqProtocolEntity):
        post_to_server('contacts/sync', self.phone_number, {'registered': resultSyncIqProtocolEntity.outNumbers.keys(),
                                                            'unregistered': resultSyncIqProtocolEntity.invalidNumbers})

    def onGetSyncError(self, errorSyncIqProtocolEntity, originalIqProtocolEntity):
        logger.info(errorSyncIqProtocolEntity)

    def init_db(self):
        url = get_env('db')
        self.db = create_engine(url, echo=False, pool_size=1, pool_timeout=600, pool_recycle=600)
        self.session = sessionmaker(bind=self.db)

    # Event handler for the layer
    def onEvent(self, event):
        if event.getName() == OngairLayer.EVENT_LOGIN:
            self.phone_number = self.getProp('ongair.account')
            self.init()
        elif event.getName() == YowNetworkLayer.EVENT_STATE_DISCONNECTED:
            logger.info('Disconnected. Will restart exit(2)')
            sys.exit(2)

    # TODO: Name therapy
    def init(self):
        # connect to the db
        self.init_db()

        # initialize the realtime notifications lib
        self._initRealtime()

        # load the account from the db
        self.get_account()

        if self.account.setup == True:
            self.setProp(YowAuthenticationProtocolLayer.PROP_CREDENTIALS,
                         (self.phone_number, self.account.whatsapp_password))
            logger.info('About to login : %s' % self.account.name)
            self.getStack().broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        else:
            logger.info('Tried to run an account that is not active')
            sys.exit(0)

    def get_account(self):
        sess = self.session()
        self.account = sess.query(Account).filter_by(phone_number=self.phone_number).scalar()
        sess.commit()

    def _post(self, url, payload):
        post_url = get_env('url') + url
        payload.update(account=self.phone_number)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.post(post_url, data=json.dumps(payload), headers=headers)

    def _sendRealtime(self, message):
        self.pubnub.publish(channel=self.channel, message=message)

    def _initRealtime(self):
        self.channel = "%s_%s" % (get_env('channel'), self.phone_number)
        self.use_realtime = True
        self.pubnub = Pubnub(get_env('pub_key'), get_env('sub_key'), None, False)
