# -*- coding: utf-8 -*-
from zope.interface import implementer, Interface
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.app.portlets.browser.editmanager import EditPortletManagerRenderer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from collective.panels.interfaces import IPanel
from collective.panels.interfaces import IManagePanelView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import (
    adapts, getMultiAdapter, queryMultiAdapter, queryAdapter, getUtility)
from AccessControl import getSecurityManager
import time
from plone.memoize.ram import cache
from zExceptions import NotFound
import logging


def addable_portlets_cache_key(function, view):
    roles = getSecurityManager().getUser().getRoles()
    return (
        set(roles),
        view.__parent__.__name__,
        view.context.__name__,
        int(time.time()) // 120,
    )


@implementer(IPortletManagerRenderer)
class EditPanelRenderer(EditPortletManagerRenderer):
    """Render a panel, which is a portlet manager, in edit mode.
    """
    adapts(Interface, IDefaultBrowserLayer, IManagePanelView, IPanel)

    template = ViewPageTemplateFile('templates/edit_panel.pt')

    @cache(addable_portlets_cache_key)
    def addable_portlets(self):
        try:
            return super(EditPanelRenderer, self).addable_portlets()
        except NotFound as exc:
            logging.getLogger("panels").warn(
                "Add-view not found for %r." % exc.message
            )
            return ()

