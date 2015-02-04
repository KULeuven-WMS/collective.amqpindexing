# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.interface.interfaces import IInterface


class ICollectiveAmqpindexingLayer(Interface):
    """Marker interface that defines a Zope 3 browser layer."""


class IMetadata(IInterface):
    """
    A Metadata to describe
    """
