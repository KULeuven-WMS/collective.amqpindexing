# -*- coding: utf-8 -*-
import unittest2
from zope import component
from plone import api
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from plone.app.testing import (helpers, TEST_USER_NAME, setRoles, TEST_USER_ID,
                               SITE_OWNER_PASSWORD, SITE_OWNER_NAME)
from collective.amqpindexing.browser.interfaces import IIndexingSettings
from collective.amqpindexing.testing import COLLECTIVE_AMQPINDEXING_FUNCTIONAL, disable_indexing, runAsyncTest


def queue_size(rabbitctl, queue_name):
    for line in rabbitctl('list_queues')[0].split('\n'):
        if queue_name in line:
            return int(line.split('\t')[1])


class TestSettings(unittest2.TestCase):
    layer = COLLECTIVE_AMQPINDEXING_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        helpers.login(self.portal, TEST_USER_NAME)
        self.browser = Browser(self.app)
        self.rabbitctl = self.layer['rabbitctl']

    def _test_queue_content(self, expected_size):
        self.assertEqual(queue_size(self.rabbitctl, 'plone.document.toindex'),
                         expected_size)

    def test_disabled_indexing(self):
        disable_indexing()
        api.content.create(
            type='Document',
            title='My Content',
            container=self.portal)
        import transaction
        transaction.commit()
        runAsyncTest(self._test_queue_content, expected_size=0, loop_timeout=3, loop_count=20)

    def test_contenttype_indexing(self):
        registry = component.getUtility(IRegistry)
        settings = registry.forInterface(IIndexingSettings)
        settings.enabled = True
        settings.indexedContentTypes = ('Event', )
        api.content.create(
            type='Document',
            title='My Content',
            container=self.portal)
        import transaction
        transaction.commit()
        api.content.create(
            type='Event',
            title='My File',
            container=self.portal)
        import transaction
        transaction.commit()
        runAsyncTest(self._test_queue_content, expected_size=2, timeout=10, loop_timeout=0.1, loop_count=5)

    def loginAsManager(self, user=SITE_OWNER_NAME, pwd=SITE_OWNER_PASSWORD):
        """points the browser to the login screen and logs in as user root with Manager role."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()
        self.assertIn("You are now logged in.", self.browser.contents)

    def test_reindex_all(self):
        self.loginAsManager()
        api.content.create(
            type='Document',
            title='My Content',
            container=self.portal)
        import transaction
        transaction.commit()
        runAsyncTest(self._test_queue_content, expected_size=2,
                     timeout=6, loop_timeout=0.1, loop_count=3)
        self.browser.open('http://nohost/plone/@@indexing-settings-controlpanel')
        self.browser.getControl(name="form.buttons.import_content").click()
        runAsyncTest(self._test_queue_content, expected_size=3,
                     timeout=6, loop_timeout=0.1, loop_count=3)

    def test_disable_indexing_form(self):
        self.loginAsManager()
        self.browser.open('http://nohost/plone/@@indexing-settings-controlpanel')
        self.browser.getControl(name='form.widgets.enabled:list').value = False
        self.browser.getControl(name="form.buttons.save").click()
        self.assertIn("Changes saved.", self.browser.contents)
        api.content.create(
            type='Document',
            title='My Content',
            container=self.portal)
        self.assertNotIn("form.buttons.import_content", self.browser.contents)
        self.browser.getControl(name='form.widgets.enabled:list').value = True
        self.browser.getControl(name="form.buttons.save").click()
        self.assertIn("Changes saved.", self.browser.contents)
        runAsyncTest(self._test_queue_content, expected_size=0,
                     timeout=6, loop_timeout=0.1, loop_count=3)
        self.browser.getControl(name="form.buttons.import_content").click()
        runAsyncTest(self._test_queue_content, expected_size=0,
                     timeout=6, loop_timeout=0.1, loop_count=3)
