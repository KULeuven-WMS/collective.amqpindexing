# -*- coding: utf-8 -*-
import asyncore
from zope import component
from zope import interface
from zope import schema
import grokcore.component as grok
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from .browser.interfaces import IIndexingSettings
from .interfaces import IMetadata
from plone.app.testing import FunctionalTesting
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

import collective.amqpindexing
from collective.zamqp.testing import ZAMQP_DEBUG_FIXTURE


def runAsyncTest(testMethod, timeout=100, loop_timeout=0.1, loop_count=1, **kwargs):
    """ Helper method for running tests requiring asyncore loop """
    while True:
        try:
            asyncore.loop(timeout=loop_timeout, count=loop_count)
            return testMethod(**kwargs)
        except AssertionError:
            if timeout > 0:
                timeout -= 1
                continue
            else:
                raise


def disable_indexing():
    registry = component.getUtility(IRegistry)
    settings = registry.forInterface(IIndexingSettings)
    settings.enabled = False


def enable_indexing():
    registry = component.getUtility(IRegistry)
    settings = registry.forInterface(IIndexingSettings)
    settings.enabled = True


class ITestMetadata(IMetadata):

    id = schema.TextLine(title=u'Unique Id of the document',
                         required=True)

    title = schema.TextLine(title=u'Title of the document',
                            required=True)

    action = schema.Choice(title=u'Action to take with the document',
                           vocabulary=schema.vocabulary.SimpleVocabulary.fromValues([u'UPDATE',
                                                                                     u'DELETE']))


class MetadataForUpdate(grok.Adapter):
    grok.implements(ITestMetadata)
    grok.context(interface.Interface)
    grok.name('update')

    action = 'UPDATE'
    type = contentPath = version = u''

    @property
    def id(self):
        return unicode(self.context.UID())

    @property
    def title(self):
        return unicode(self.context.Title(), 'utf-8')


class MetadataForDelete(MetadataForUpdate):
    grok.implements(ITestMetadata)
    grok.context(interface.Interface)
    grok.name('delete')

    action = 'DELETE'


class MetadataForCreate(MetadataForUpdate):
    grok.implements(ITestMetadata)
    grok.context(interface.Interface)
    grok.name('create')

    action = 'CREATE'


class IndexingFixtureLayer(PloneWithPackageLayer):

    def setUpPloneSite(self, portal):
        from collective.indexing import monkey
        monkey
        super(IndexingFixtureLayer, self).setUpPloneSite(portal)
        enable_indexing()

COLLECTIVE_AMQPINDEXING = IndexingFixtureLayer(
    zcml_package=collective.amqpindexing,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.amqpindexing:default',
    name='COLLECTIVE_AMQPINDEXING')

COLLECTIVE_AMQPINDEXING_INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_AMQPINDEXING, ZAMQP_DEBUG_FIXTURE),
    name="COLLECTIVE_AMQPINDEXING_INTEGRATION")

COLLECTIVE_AMQPINDEXING_FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_AMQPINDEXING, ZAMQP_DEBUG_FIXTURE),
    name="COLLECTIVE_AMQPINDEXING_FUNCTIONAL")

COLLECTIVE_AMQPINDEXING_ROBOT_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_AMQPINDEXING, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="COLLECTIVE_AMQPINDEXING_ROBOT_TESTING")
