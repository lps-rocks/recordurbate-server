#!/usr/bin/python3
import socketserver
import http.server
import urllib.parse
from subprocess import check_output
import json
import sys
import config as Config
from bot import Bot
import logging
import re
import threading

#processes = []
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.WARNING)
logger.addHandler(out_hdlr)

class BotThread(threading.Thread):
    def __init__(self, nom = ''):
        threading.Thread.__init__(self)
        self.bot = SuperBot(logger)

    def run(self):
        self.bot.running = True
        self.bot.run()

    def stop(self):
        self.bot.running = False

    def recording(self):
        recording = []
        for idx, rec in enumerate(self.bot.processes):
          recording.append(rec[0])
        return recording

class SuperBot(Bot):
    def __init__(self, logger):
        self.logger = logger
        self.reload_config()
    def run(self):
        Bot.run(self)
        self.processes = []

t = None

def start_new_thread():
    global t
    t = BotThread()
    t.start()

class Handler(http.server.SimpleHTTPRequestHandler):
    def dispatch(self, method):
        try:
            path = urllib.parse.urlparse(self.path).path

            streamerNamePath = re.compile('^/streamers/(.*)')
            streamerNamePathMatch = streamerNamePath.match(path)
            config = Config.load_config()

            if path == '/status'    and method == 'GET':
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps('ON' if t.is_alive() else 'OFF'), 'utf8'))
            elif path == '/status'    and method == 'PUT':
                content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
                status = self.rfile.read(content_length).decode('utf-8') # <--- Gets the data itself
                if (status == 'ON' or status == '"ON"'):
                    if (not t.is_alive()):
                        start_new_thread()
                    self.send_response(204)
                    self.end_headers()
                elif (status == 'OFF' or status == '"OFF"'):
                    if (t.is_alive()):
                        t.stop()
                    self.send_response(204)
                    self.end_headers()
                else:
                    self.send_response(400)
                    self.end_headers()
            elif path == '/recording' and method == 'GET':
                recording = t.recording()
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(recording), 'utf8'))
            elif path == '/streamers' and method == 'GET':
                self.send_response(200)
                self.send_header('Content-type','application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(config['streamers']), 'utf8'))
            elif streamerNamePathMatch != None and method == 'PUT':
                username = streamerNamePathMatch.group(1).lower()
                idx = Config.find_in_config(username, config)

                if idx == None:
                  config["streamers"].append(username)
                  Config.save_config(config)

                self.send_response(204)
                self.end_headers()
            elif streamerNamePathMatch != None and method == 'DELETE':
                username = streamerNamePathMatch.group(1).lower()
                idx = Config.find_in_config(username, config)

                if not idx == None:
                  del config["streamers"][idx]
                  Config.save_config(config)

                self.send_response(204)
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        except Exception as inst:
            self.send_response(500)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write(bytes(str(inst), 'utf8'))
            print('ERROR ' + str(inst))

    def do_PUT(self):
        self.dispatch('PUT')

    def do_GET(self):
        self.dispatch('GET')

    def do_DELETE(self):
        self.dispatch('DELETE')

if __name__ == "__main__":
  httpd = socketserver.TCPServer(('', 5599), Handler)
  try:
     start_new_thread()
     print('Listening')
     httpd.serve_forever()
  except KeyboardInterrupt:
     pass
  httpd.server_close()
  print('Ended')
