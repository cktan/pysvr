#!/usr/bin/env python2.7
import sys, os, json
import bottle
from bottle import route, run, request, abort, default_app

scriptdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(scriptdir, '..', 'lib'))
print sys.path
import conf, plog

plog.info('started')

# see slide 33 at http://www.slideshare.net/apigee/restful-api-design-second-edition?ref= 
# for explanation about the API 

@route('/dogs', method='POST')
@route('/dogs/', method='POST')
def create_new_dog():
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    entity = json.loads(data)
    if not entity.has_key('name'):
        abort(400, 'No name specified')

    return 'NEW DOG %s\n' % str(entity['name'])


@route('/dogs', method='GET')
@route('/dogs/', method='GET')
def list_dogs():
    return 'LIST DOGS\n'

@route('/dogs', method='DELETE')
@route('/dogs/', method='DELETE')
def delete_all_dogs():
    return 'DELETE ALL DOGS\n'

@route('/dogs/:name', method='GET')
def show_dog(name):
    return 'SHOW DOG %s\n' % name

@route('/dogs/:name', method='DELETE')
def delete_dog(name):
    return "DELETE DOG %s\n" % name

@route('/dogs/:name', method='PUT')
def update_dog(name):
    return 'UPDATE DOG %s\n' % name

if __name__ == "__main__":
    run(host="localhost", port=8081)
else:
    application = default_app()

