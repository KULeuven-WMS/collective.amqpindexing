# -*- coding: utf-8 -*-
from zope import component
from zope import interface
from collective.indexing.interfaces import IIndexQueueProcessor
from collective.zamqp.interfaces import IProducer
from .metadata import _extract_metadata
from .changes import should_index_content


def publish(indexed_content):
    producer = component.getUtility(IProducer, name='document')
    producer.register()
    producer.publish(indexed_content)


class AMQPIndexProcessor(object):
    interface.implements(IIndexQueueProcessor)

    def __init__(self, manager=None):
        self.manager = manager

    def index(self, obj, attributes=None):
        if should_index_content(obj):
            payload = _extract_metadata(obj, 'create')
            publish(payload)

    def reindex(self, obj, attributes=None):
        if should_index_content(obj):
            payload = _extract_metadata(obj, 'update')
            publish(payload)

    def unindex(self, obj):
        if should_index_content(obj):
            payload = _extract_metadata(obj, 'delete')
            publish(payload)

    def begin(self):
        """collective zamqp publisher has its own TM, nothing to do here"""

    def commit(self, wait=None):
        """collective zamqp publisher has its own TM, nothing to do here"""

    def abort(self):
        """collective zamqp publisher has its own TM, nothing to do here"""
