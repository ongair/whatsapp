import os, logging, json, requests

def get_env(key):
  return os.environ.get(key).encode('utf-8')

def setup_logging(phone_number):
  # logging.captureWarnings(True)
  env = get_env('env')  
  logging.basicConfig(level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M',
    filename="%s/logs/%s.%s.log" %(get_env('pwd'), phone_number, env),
    filemode='w')

def post_to_server(url, phone_number, payload):
  post_url = get_env('url') + url
  payload.update(account = phone_number)
  headers = { 'Content-Type' : 'application/json', 'Accept' : 'application/json' }
  response = requests.post(post_url, data=json.dumps(payload), headers=headers)
