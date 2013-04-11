#!/usr/bin/env python2.7
import sys, os, json
import bottle
from bottle import route, run, request, abort, default_app

scriptdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(scriptdir, '..', 'lib'))
print sys.path
import conf, plog

plog.info('started')

@route('/documents', method='PUT')
def new_document():
    data = request.body.readline()
    if not data:
        abort(400, 'No data received')
    entity = json.loads(data)
    if not entity.has_key('_id'):
        abort(400, 'No _id specified')

    return 'NEW DOCUMENT ' + str(entity['_id'])

@route('/documents/:id', method='POST')
def replace_document(id):
    return 'REPLACE DOCUMENT ' + id

@route('/documents/:id', method='DELETE')
def delete_document(id):
    return 'DELETE ' + id

@route('/documents/')
def list_document():
    return 'LIST DOCUMENTS'

@route('/documents/:id')
def get_document(id):
    return 'GET DOCUMENT ' + id


if __name__ == "__main__":
    run(host="localhost", port=8081)
else:
    application = default_app()

