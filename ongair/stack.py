from yowsup.stacks import YowStackBuilder, YowStack
from yowsup.layers import YowLayer, YowParallelLayer
from yowsup.layers.auth                        import YowCryptLayer, YowAuthenticationProtocolLayer
from yowsup.layers.coder                       import YowCoderLayer
from yowsup.layers.logger                      import YowLoggerLayer
from yowsup.layers.network                     import YowNetworkLayer
from yowsup.layers.protocol_messages           import YowMessagesProtocolLayer
from yowsup.layers.stanzaregulator             import YowStanzaRegulator
from yowsup.layers.protocol_media              import YowMediaProtocolLayer
from yowsup.layers.protocol_acks               import YowAckProtocolLayer
from yowsup.layers.protocol_receipts           import YowReceiptProtocolLayer
from yowsup.layers.protocol_groups             import YowGroupsProtocolLayer
from yowsup.layers.protocol_presence           import YowPresenceProtocolLayer
from yowsup.layers.protocol_ib                 import YowIbProtocolLayer
from yowsup.layers.protocol_notifications      import YowNotificationsProtocolLayer
from yowsup.layers.protocol_iq                 import YowIqProtocolLayer
from yowsup.layers.protocol_contacts           import YowContactsIqProtocolLayer
from yowsup.layers.protocol_chatstate          import YowChatstateProtocolLayer
from yowsup.layers.protocol_privacy            import YowPrivacyProtocolLayer
from yowsup.layers.protocol_profiles           import YowProfilesProtocolLayer
from yowsup.layers.protocol_calls import YowCallsProtocolLayer
from notification import OngairYowNotificationsProtocolLayer

class OngairStackBuilder():

  ONGAIR_YOWSUP_PROTOCOL_LAYERS_BASIC = (
    YowAuthenticationProtocolLayer, YowMessagesProtocolLayer,
    YowReceiptProtocolLayer, YowAckProtocolLayer, YowPresenceProtocolLayer,
    YowIbProtocolLayer, YowIqProtocolLayer, OngairYowNotificationsProtocolLayer,
    YowContactsIqProtocolLayer, YowChatstateProtocolLayer, YowCallsProtocolLayer
  )

  def __init__(self):
    self.layers = ()
    self._props = {}

  def pushDefaultLayers(self):
    defaultLayers = self.getDefaultLayers()
    self.layers += defaultLayers
    return self        

  def push(self, yowLayer):
    self.layers += (yowLayer,)
    return self

  def build(self):
    return YowStack(self.layers, reversed = False, props = self._props)


  def getDefaultLayers(self, groups = True, media = True, privacy = True, profiles = True):
    coreLayers = YowStackBuilder.getCoreLayers()
    protocolLayers = YowStackBuilder.getProtocolLayers(groups = groups, media=media, privacy=privacy, profiles=profiles)

    allLayers = coreLayers    
    allLayers += (YowParallelLayer(protocolLayers),)

    return allLayers

  def getProtocolLayers(self, groups = True, media = True, privacy = True, profiles = True):
    layers = ONGAIR_YOWSUP_PROTOCOL_LAYERS_BASIC
    if groups:
      layers += (YowGroupsProtocolLayer,)

    if media:
      layers += (YowMediaProtocolLayer, )

    if privacy:
      layers += (YowPrivacyProtocolLayer, )

    if profiles:
      layers += (YowProfilesProtocolLayer, )

    return layers