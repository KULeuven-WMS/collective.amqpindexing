# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.elasticindex')


class IIndexingSettings(Interface):

    enabled = schema.Bool(
        title=_(u'Enable Enterprise Search Indexing ?'),
        default=False)

    indexedContentTypes = schema.Tuple(
        title=_(u"Content types to index"),
        description=_(u"List content types which should be indexed"),
        value_type=schema.ASCIILine(title=_(u"Content type name")),
        default=('File', 'Image', 'News Item', ))
