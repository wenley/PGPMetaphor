
# Requires you to `pip install python-gnupg`

from flask import Flask
from flask import request
app = Flask(__name__)

from gnupg import GPG
gpg = GPG()

import json

@app.route("/metaphors/")
def metaphorIndex():
  with open('metaphor_index.html') as f:
    s = f.read()
  return s

@app.route("/start_send_task")
def inital_data_for_sending():
  return json.dumps({
    'alice': 0,
    'bob': 1,
    'message': "Hey Alice, want to talk secretly at the secret place at 10 pm tonight?",
    })

@app.route("/start_verify_message")
def inital_data_for_verifying():
  message = "Hey, the NSA is onto us. Get packed and meet me at the drop zone."
  encrypted = str(gpg.encrypt(message, gpg.keys[2]))
  signed = str(gpg.sign(encrypted, keyid=gpg.keys[1]))
  return json.dumps({
    'ciphertext': signed,
    'alice': 0,
    'bob': 1,
    'me': 2,
    })

@app.route("/finished")
def finish_task():
  logs = request.form['logs']
  return "OK"

@app.route("/action", methods=["POST"])
def do_action():
  obj = request.form['object']
  fingerprint = gpg.keys[request.form['key_index']]
  action = request.form['action']
  data = request.form['data']
  if action == 'lock':
    ciphertext = gpg.encrypt(data, fingerprint)
    return json.dumps({ 'data': str(ciphertext) })
  elif action == 'sign':
    signed_text = gpg.sign(data, keyid=fingerprint)
    return json.dumps({ 'data': str(signed_text) })
  elif action == 'unlock':
    pass
  elif action == 'verify':
    if obj == 'image' and fingerprint == gpg.keys[1]:
      return json.dumps({ 'verified': True })
    else:
      return json.dumps({ 'verified': False })
  else:
    return "unrecognized action. Please restart and try again."

@app.route('/new_key', methods=["POST"])
def choose_new_key():
  '''
  Expects POST with list field 'taken_keys' that
  contains the fingerprints of the keys that are
  already taken.
  '''
  taken_keys = request.form['taken_keys']

def initialize_gpg():
  num_keys = len(gpg.list_keys())
  for i in xrange(num_keys, 50):
    key_input = gpg.gen_key_input(key_type="RSA", key_length=2048)
    key = gpg.gen_key(key_input)

  # Adds field for quick access to fingerprints
  gpg.keys = [k['fingerprint'] for k in gpg.list_keys(True)]

if __name__ == "__main__":
  initialize_gpg()
  app.run()
