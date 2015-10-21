import requests
# import redis
import os
import mandrill 
from os.path import join, dirname
from dotenv import load_dotenv

def check_status(token):
  url = "https://upload.uploadcare.com/from_url/status/?token=%s" %token

  response = requests.get(url)
  result_json = response.json()

  ready = result_json['status'] and result_json['is_ready']
  if ready:
    return "http://www.ucarecdn.com/%s/%s" %(result_json['file_id'], result_json['original_filename'])
  else:
    return False

def save_file(url):
  upload_url = "https://upload.uploadcare.com/from_url/?pub_key=%s&store=0&source_url=%s" %(os.environ.get('uploadcare_public_key'), url)
  response = requests.post(url)  

  token = result_json['token']
  return token

def construct(email):
  return { 'email': email }

def email(url, phone_number):
  try:
    mandrill_client = mandrill.Mandrill(os.environ.get('mandrill_api_key').encode('utf8'))
    cc_list = os.environ.get('video_ccc_email').encode('utf8').split(',')
    cc_list.append(os.environ.get('video_to_email'))

    mails = map(construct, cc_list)
    print mails
    message = {
      'from_email' : os.environ.get('video_from_email').encode('utf8'),
      'from_name' : 'Ongair Media',
      'headers': {'Reply-To': os.environ.get('video_from_email').encode('utf8') },
      'subject': 'Persil Video from %s' %phone_number,
      'html': "<p>A video whas been sent to you via WhatsApp from %s.<br />Please download within 24 hours from <a href='%s'>here</a>.</p>" %(phone_number, url),
      'to' : mails
    }

    result = mandrill_client.messages.send(message=message, async=False, ip_pool='Main Pool') 
  except mandrill.Error, e:
    print 'A mandrill error occurred: %s - %s' % (e.__class__, e)