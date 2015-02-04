# -*- coding: utf-8 -*-
import json
import unittest2
from zope import interface
from plone import api
from plone.app.testing import helpers, TEST_USER_NAME, setRoles, TEST_USER_ID
from collective.amqpindexing.metadata import _extract_metadata
from collective.amqpindexing.testing import COLLECTIVE_AMQPINDEXING_FUNCTIONAL


class TestMetadataExtraction(unittest2.TestCase):
    layer = COLLECTIVE_AMQPINDEXING_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        helpers.login(self.portal, TEST_USER_NAME)

    def test_extraction_update_dummy_object(self):
        with self.assertRaises(interface.Invalid):
            _extract_metadata(object(), 'update')

    def test_document_metadata(self):
        doc = api.content.create(
            type='Document',
            id='my-content',
            title='My Content',
            container=self.portal)
        self.assertEqual(api.content.get_state(obj=doc), 'visible')
        metadata_json = _extract_metadata(doc, 'update')
        metadata = json.loads(metadata_json)
        plone_metadata = metadata['source']
        self.assertEqual(metadata[u'action'], u'UPDATE')
        self.assertEqual(plone_metadata[u'title'], u'My Content')
        self.assertEqual(plone_metadata[u'url'], u'http://nohost/plone/my-content')
        self.assertEqual(plone_metadata[u'metaType'], u'Document')
        self.assertEqual(plone_metadata[u'contenttype'], u'text/html')
        self.assertEqual(plone_metadata[u'content'], u'my-content  My Content ')
        self.assertEqual(plone_metadata["authorizedUsers"], [u'Anonymous'])
        api.content.transition(obj=doc, transition='hide')
        metadata_json = _extract_metadata(doc, 'update')
        metadata = json.loads(metadata_json)
        plone_metadata = metadata['source']
        self.assertEqual(plone_metadata["authorizedUsers"],
                         [u'user:test_user_1_',
                          u'Site Administrator',
                          u'Manager',
                          u'user:admin',
                          u'Editor',
                          u'Reader',
                          u'Contributor'])
