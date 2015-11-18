import os, logging, json, requests, posixpath, urlparse, urllib

logger = logging.getLogger(__name__)

def get_env(key):
  return os.environ.get(key).encode('utf-8')

def get_filename(url):
  path = urlparse.urlsplit(url).path
  return posixpath.basename(path)

def download(url, name=None):
  if name is None:
    filename = get_filename(url)
  else:
    filename = name
  logger.info("About to download %s to tmp/%s" %(url, filename))
  urllib.urlretrieve (url, "tmp/%s" %filename)
  return "tmp/%s" %filename

def setup_logging(phone_number):
  # logging.captureWarnings(True)
  env = get_env('env')  
  logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename="%s/logs/%s.%s.log" %(get_env('pwd'), phone_number, env),
    filemode='a')

def post_to_server(url, phone_number, payload):
  try:
    post_url = get_env('url') + url
    payload.update(account = phone_number)
    headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json' }
    response = requests.post(post_url, data=json.dumps(payload), headers=headers)
  except:
    logger.info('Error with reaching the url %s' %url)

def send_sms(to, message):

  try:
    post_url = get_env('sms_gateway_url')    
    requests.post(post_url, data={ 'phone_number' : to, 'message': message} )
  except:
    logger.info('Error with reaching the url %s' %post_url)

def normalizeJid(number):
  if '@' in number:
    return number
  elif "-" in number:
    return "%s@g.us" % number

  return "%s@s.whatsapp.net" % number