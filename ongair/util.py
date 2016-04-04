import os, logging, json, requests, posixpath, urlparse, urllib

logger = logging.getLogger(__name__)


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


# This function extracts a file name from looking at the last part of the url
def get_filename(url):
    path = urlparse.urlsplit(url).path
    return posixpath.basename(path)


# This function downloads a file to the temporary folder and returns the path
def download(url, name=None):
    # If no name is provided use the last part of the url
    if name is None:
        filename = get_filename(url)
    else:
        filename = name

    logger.info("About to download %s to tmp/%s" % (url, filename))
    urllib.urlretrieve(url, "tmp/%s" % filename)

    # return the path of the file
    return "tmp/%s" % filename


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
