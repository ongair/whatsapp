from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from uploader import email

class VideoUploadLayer(YowInterfaceLayer):
  @ProtocolEntityCallback("message")
  def onMessage(self, messageProtocolEntity):
    if messageProtocolEntity.getType() == 'media':
      self.onMediaMessage(messageProtocolEntity)

    # send receipts lower
    self.toLower(messageProtocolEntity.ack())
    # self.toLower(messageProtocolEntity.ack(True))
    

  @ProtocolEntityCallback("receipt")
  def onReceipt(self, entity):
    self.toLower(entity.ack())

  def onMediaMessage(self, messageProtocolEntity):
    if messageProtocolEntity.getMediaType() == "video":
      email(messageProtocolEntity.url, messageProtocolEntity.getFrom(False))