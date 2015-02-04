# -*- coding: utf-8 -*-
from zope import component
from z3c.form import button, form
from plone.registry.interfaces import IRegistry
from plone.app.registry.browser import controlpanel
from Products.statusmessages.interfaces import IStatusMessage
from .interfaces import IIndexingSettings
from ..changes import (list_content, index_content, should_index_content)


class IndexingSettingsForm(controlpanel.RegistryEditForm):
    label = u"AMQP Indexing setttings"
    schema = IIndexingSettings
    form.extends(controlpanel.RegistryEditForm)

    def index_plonesite(self):
        plonesite = self.context
        for item in list_content(plonesite):
            if should_index_content(item):
                index_content(item)

    @property
    def is_indexing_enabled(self):
        registry = component.getUtility(IRegistry)
        settings = registry.forInterface(IIndexingSettings)
        return settings.enabled

    @button.buttonAndHandler(u'Import site content', name='import_content',
                             condition=lambda form: form.is_indexing_enabled)
    def import_site_content(self, action):
        send = IStatusMessage(self.request).add
        try:
            self.index_plonesite()
        except:
            send("Error while indexing the site.", type='error')
        else:
            send("Site indexed successfully.")


class IndexingSettings(controlpanel.ControlPanelFormWrapper):
    form = IndexingSettingsForm
