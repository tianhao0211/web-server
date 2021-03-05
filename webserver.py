import os
from os import curdir
from os.path import join as pjoin
import json
from datetime import datetime
#from http.server import BaseHTTPRequestHandler, HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

PORT = 8080
FILE = 'store.json'

# initialize the storage file if file does not exist yet (this will create the storage file when 1st run)
if os.path.exists(FILE) == 0:
    with open(FILE, 'w') as f:
        f.write('{}')


class StoreHandler(BaseHTTPRequestHandler):
    store_path = pjoin(curdir, FILE)

    # define the GET action
    def do_GET(self):
        if self.path.find("/conversations/") != -1:
            # get last variable, which is the key - conversation_id
            key = self.path.split("/conversations/")[-1]
            # open the store.json file and read content under the key (conversation_id)
            with open(self.store_path, 'r') as fh:
                data = json.loads(fh.read())
                result = data.get(key, [])

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # pretty printing the output
            self.wfile.write(json.dumps({'id':key,'messages':result},sort_keys=True, indent=4).encode())
        else:
            # return 404 error if the curl url is invalid
            self.send_response(404)


    # define the POST action
    def do_POST(self):
        # with or without the forward slash, both situations are considered to be valid
        if self.path == '/messages' or self.path == '/messages/':
            length = self.headers['content-length']
            data = json.loads(self.rfile.read(int(length)))
            # add the created time in the POST data, use specific format as instructed
            time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z'
            data['created'] = time

            # write the new data into sotrage file, with checking if the conversation_id exists in chat history
            key = data["conversation_id"]
            del data["conversation_id"]
            with open(self.store_path, 'r') as fh:
                db = json.loads(fh.read())
            with open(self.store_path, 'w') as fh:
                # if conversation_id exist, inject the data under the same JSON object
                if key not in db:
                    db[key] = [data]
                # if not, append the data as a new JSON object
                else:
                    db[key].append(data)

                fh.write(json.dumps(db)+'\n')
            self.send_response(200)
        else:
            # return 404 error if the curl url is invalid
            self.send_response(404)


server = HTTPServer(('', PORT), StoreHandler)
print 'Starting httpd on port: ', PORT
print 'Use curl command to test GET and POST actions'
server.serve_forever()
