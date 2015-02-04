# -*- coding: utf-8 -*-
from zope import component, schema
from AccessControl.PermissionRole import rolesForPermissionOn
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.utils import getToolByName
from z3c.schema2json import serialize
from .interfaces import IMetadata


def get_security(content):
    """Return a list of roles and users with View permission.
    Used to filter out items you're not allowed to see.
    """
    allowed = {unicode(r) for r in set(rolesForPermissionOn('View', content))}
    # shortcut roles and only index the most basic system role if the object
    # is viewable by either of those
    if 'Anonymous' in allowed:
        return set([u'Anonymous'])
    elif 'Authenticated' in allowed:
        return set([u'Authenticated'])
    try:
        acl_users = getToolByName(content, 'acl_users', None)
        if acl_users is not None:
            local_roles = acl_users._getAllLocalRoles(content)
    except AttributeError:
        local_roles = _mergedLocalRoles(content)
    for user, roles in local_roles.items():
        for role in roles:
            if role in allowed:
                allowed.add(u'user:' + user)
    if 'Owner' in allowed:
        allowed.remove('Owner')
    return allowed


def _extract_metadata(context, action):
    gsm = component.getGlobalSiteManager()
    # is this the right way to fetch the registered Interface ?
    interfaces = [interface for interfaceName, interface in
                  gsm.getUtilitiesFor(IMetadata)]
    metadataInterface = interfaces[0]
    metadata = component.getAdapter(context, metadataInterface, name=action)
    errors = schema.getValidationErrors(IMetadata, metadata)
    if errors:
        raise interface.Invalid(errors)
    payload = serialize(metadataInterface, metadata)
    return payload
