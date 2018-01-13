from Products.CMFCore.interfaces import ISiteRoot
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.registry.interfaces import IRegistry
from zope.component import ComponentLookupError
from zope.component import getUtility
from collective.panels.interfaces import IGlobalSettings


def root_interface():
    root_interface = ISiteRoot
    try:
        settings = getUtility(IRegistry).forInterface(IGlobalSettings)
    except (ComponentLookupError, KeyError):
        pass
    else:
        if settings.navigation_local:
            root_interface = INavigationRoot
    return root_interface


def encode(name):
    return name.replace('.', '-')


def decode(name):
    return name.replace('-', '.')

