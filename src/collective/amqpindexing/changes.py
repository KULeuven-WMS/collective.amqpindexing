from zope import component
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import IFolderish, IContentish
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.zamqp.interfaces import IProducer
from .metadata import _extract_metadata
from .browser.interfaces import IIndexingSettings


def should_index_content(context):
    if IPloneSiteRoot.providedBy(context):
        return False
    if IFolderish.providedBy(context) and not should_index_container(context):
        return False
    registry = component.getUtility(IRegistry)
    try:
        settings = registry.forInterface(IIndexingSettings)
        return settings.enabled and context.portal_type in settings.indexedContentTypes
    except KeyError:
        return False


def should_index_container(context):
    # XXX some container should be indexed ?
    return False


def publish(indexed_content):
    producer = component.getUtility(IProducer, name='document')
    producer.register()
    producer.publish(indexed_content)


def index_content(context):
    payload = _extract_metadata(context, 'update')
    publish(payload)


def unindex_content(context):
    payload = _extract_metadata(context, 'delete')
    publish(payload)


def list_content(content):
    """Recursively list CMF content out of the given one. ``callback``
    is called every thousand items after a commit.
    """

    def recurse(content):
        for child in content.contentValues():
            if IFolderish.providedBy(child):
                for grandchild in recurse(child):
                    yield grandchild
            yield child

    if IFolderish.providedBy(content):
        for child in recurse(content):
            yield child
        yield content
    elif IContentish.providedBy(content):
        yield content
