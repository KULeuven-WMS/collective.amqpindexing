# -*- coding: utf-8 -*-
import json
from collective.zamqp.producer import Producer
import grokcore.component as grok


def reduce_identical_messages(messages):
    known_uids = []
    for i, message in enumerate(messages):
        message_body = json.loads(message['body'])
        object_uid = message_body['id']
        if object_uid in known_uids:
            messages.pop(i)
        known_uids.append(object_uid)


class IndexedDocumentPublisher(Producer):
    grok.name('document')
    connection_id = 'rabbit'
    exchange = 'plone.document'
    queue = 'plone.document.toindex'
    serializer = 'text'
    durable = True

    def _finish(self):
        reduce_identical_messages(self._pending_messages)
        Producer._finish(self)
