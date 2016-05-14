import os, logging, json, requests, posixpath, urlparse, urllib
import string, random, urllib2, magic, mimetypes, rollbar, traceback

logger = logging.getLogger(__name__)

# Generate a random file name
def name_generator(size=20, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# Get an environment variable
def get_env(key, raiseError=True, default_value=None):
    value = os.environ.get(key)
    if value is None:
        if raiseError:
            raise Exception("Error. Environment Variables not loaded, kindly load them " % key)
        else:
            return default_value
    else:
        return value.encode('utf-8')

# This function downloads a file to the temporary folder and returns the path
def download(url):
    try:
        image_data = urllib2.urlopen(url).read()
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as mg:
            mime_type = mg.id_buffer(image_data)
            mimetypes.init()
            
            ext = mimetypes.guess_extension(mime_type)
            
            filename = "tmp/%s%s" %(name_generator(), ext)

            file = open(filename, "w")
            file.write(image_data)
            file.close()
            return filename
    except Exception as ex:
        rollbar.report_exc_info()        
        return None

# This function removes a file from tmp
def cleanup_file(path):
    os.remove(path)

def setup_logging(phone_number):
    # logging.captureWarnings(True)
    env = get_env('env')
    verbose = get_env('verbose', False)

    # customize the log level from the environment
    level = logging.DEBUG if verbose == "True" else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename="%s/logs/%s.%s.log" % (get_env('pwd'), phone_number, env),
                        filemode='a')

def post_to_server(url, phone_number, payload):
    try:
        post_url = get_env('url') + url
        payload.update(account=phone_number)
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        response = requests.post(post_url, data=json.dumps(payload), headers=headers)
    except:
        logger.info('Error with reaching the url %s' % url)

# Sends a notification to slack
def notify_slack(message, channel="#activation", username="webhookbot"):
    url = "https://ongair.slack.com/services/hooks/incoming-webhook?token=%s" % get_env('slack_token')
    try:
        data = json.dumps({ 'channel': channel, 'username': username, 'icon_emoji' : ':ghost:', 'text' : message })
        requests.post(url, data=data)
    except:
        logger.exception("Error posting to slack")
        rollbar.report_exc_info()

def send_sms(to, message):
    try:
        post_url = get_env('sms_gateway_url')
        requests.post(post_url, data={'phone_number': to, 'message': message})
    except:
        logger.info('Error with reaching the url %s' % post_url)

def normalizeJid(number):
    if '@' in number:
        return number
    elif "-" in number:
        return "%s@g.us" % number

    return "%s@s.whatsapp.net" % number


# Removes the @s.whatsapp.net from a jid
def strip_jid(jid):
    return jid.split('@')[0]
