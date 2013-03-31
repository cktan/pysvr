#!/usr/bin/env python
import json
import bottle
from bottle import route, run, request, abort, default_app

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

