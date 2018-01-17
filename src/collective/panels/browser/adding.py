# -*- coding: utf-8 -*-
from warnings import warn

from zope.interface import implementer
from zope.component import getMultiAdapter

from zope.container.interfaces import INameChooser

from Acquisition import aq_inner, aq_base, aq_parent
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from collective.panels.interfaces import IPanelAdding
from plone.app.portlets.interfaces import IPortletPermissionChecker
from Products.statusmessages.interfaces import IStatusMessage
from AccessControl import Unauthorized
from collective.panels import _
from Products.CMFPlone.utils import safe_unicode


class PanelAdding(BrowserView):

    def authorize(self):
        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u"authenticator")
        if not authenticator.verify():
            raise Unauthorized

    def __call__(self):
        self.authorize()
        self.add()
        return self.request.response.redirect(self.nextURL())


    def add(self):
        """Add the panel to the panel manager
        """
        context = aq_inner(self.context)
        manager = aq_base(context)

        # todo
        IPortletPermissionChecker(context)()

        layout = self.request.get('layout', '')
        if not layout:
            raise BadRequest("Missing layout.")
        css_class = self.request.get('css_class', '')
        heading = safe_unicode(self.request.get('heading', ''))

        manager.addPanel(layout, css_class, heading)

        IStatusMessage(self.request).addStatusMessage(
            _(u"Panel added."), type="info")


    @property
    def referer(self):
        return self.request.get('referer', '')

    def nextURL(self):
        urltool = getToolByName(self.context, 'portal_url')
        referer = self.referer
        if not referer or not urltool.isURLInPortal(referer):
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request),
                                      name=u"absolute_url"))
            # todo: better fallback
            referer = url + '/@@manage-panels'
        return referer
