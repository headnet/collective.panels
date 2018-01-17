# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.layout.viewlets import ViewletBase
from collective.panels.utils import root_interface
from collective.panels.interfaces import IGlobalSettings
from zope.component import ComponentLookupError
from zope.security import checkPermission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.panels import _
from collective.panels.interfaces import IGlobalSettings
from collective.panels.interfaces import ILayout
from collective.panels.interfaces import IPanel
from collective.panels.traversal import PanelManager
from plone.app.portlets.manager import ColumnPortletManagerRenderer
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.utils import hashPortletInfo
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from zope.component import ComponentLookupError
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility

import logging


def render_portlets_in_layout(portlets, layout_name, request):
    """ Render portlets in a layout
    """
    namespace = {'portlets': portlets}
    try:
        layout = getAdapter(request, ILayout, name=layout_name)
    except ComponentLookupError:
        return _(u"Missing layout: ${layout_name}.",
                 mapping={'layout_name': layout_name})

    template = layout['template']
    return template.pt_render(namespace)


class DisplayPanelView(BrowserView):
    """This view displays a panel."""

    render_portlet = ViewPageTemplateFile("templates/portlet.pt")
    error_message = ColumnPortletManagerRenderer.__dict__['error_message']

    def __init__(self, context, request):
        super(DisplayPanelView, self).__init__(context, request)

        # todo: move away from init

        # The parent object is the Plone content object here; we get
        # it from the acquisition chain.

        # The panel can be rendered in different contexts, where the length of
        # the chain to the Plone content object is not obvious;
        # on portlet edit forms for instance, where we have a panel of
        # portlets below the edit form.
        # So to get the content object we go up in the aq chain, until we are
        # out of the chain of portlet assignments, panels etc.
        parent = self.context.aq_inner
        while True:
            parent = parent.aq_parent
            if not (IPanel.providedBy(parent)
                or IPortletAssignment.providedBy(parent)
                or IPortletAssignmentMapping.providedBy(parent)):
                break

        panel = self.context

        portlets = []
        for assignment in panel:
            settings = IPortletAssignmentSettings(assignment)
            if not settings.get('visible', True):
                continue

            try:
                portlet = getMultiAdapter(
                    (parent,
                     self.request,
                     self,
                     panel,
                     assignment), IPortletRenderer)
            except ComponentLookupError:
                logging.getLogger("panels").info(
                    "unable to look up renderer for '%s.%s'." % (
                        assignment.__class__.__module__,
                        assignment.__class__.__name__
                    )
                )
                continue

            info = {
                'manager': "panels",
                'category': CONTEXT_CATEGORY,
                'key': str('/'.join(parent.getPhysicalPath())),
                'name': assignment.__name__,
                'renderer': portlet,
                'settings': settings,
                'assignment': assignment
            }

            # todo: check new impl. of portlet rendering
            hashPortletInfo(info)

            portlet.__portlet_metadata__ = info.copy()
            del portlet.__portlet_metadata__['renderer']

            portlet.update()

            try:
                available = portlet.available
            except ConflictError:
                raise
            except Exception as err:
                logging.getLogger('panels').info(
                    "available threw an exception for %s (%s %s)" % (
                        assignment.__name__,
                        type(err),
                        str(err)
                    )
                )
                continue

            info['available'] = available
            portlets.append(info)

        self.portlets = portlets

    def render_panel(self, mapper=lambda f, ds: [f(**d) for d in ds if d['available']]):
        columns = list(mapper(self.render_portlet, self.portlets))
        return render_portlets_in_layout(columns, self.context.layout, self.request)

    def safe_render_portlet(self, renderer):
        try:
            return renderer.render()
        except ConflictError:
            raise
        except Exception:
            logging.getLogger("panels").exception(
                'Error while rendering %r' % (self, )
            )

            return self.error_message()


class BaseViewlet(ViewletBase):

    def __init__(self, context, request, view, manager=None):
        super(BaseViewlet, self).__init__(
            context, request, view, manager
        )

        self.root_interface = root_interface()


class DisplayPanelManagerViewlet(BaseViewlet):
    """ This viewlet renders all panels in a panel manager
    """
    index = ViewPageTemplateFile("templates/display_panel_manager.pt")

    @property
    def normalized_manager_name(self):
        # Get the viewlet manager name. It is also used as the panel manager
        # name.
        # todo - this is not normalized
        return self.manager.__name__

    @property
    def panels(self):
        location = self.context

        try:
            settings = getUtility(IRegistry).forInterface(IGlobalSettings)
        except ComponentLookupError:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Unable to find registry."), type="error"
            )
        except KeyError:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Global panel settings unavailable; ignoring."),
                type="warning"
            )
        else:
            # If the panel manager interfaces (aka viewlet managers) are
            # defined as site-only or navigation-root-only in the settings,
            # go up the aq_chain to find the panel definition location.
            for interface in settings.site_local_managers or ():
                if interface.providedBy(self.manager):
                    while not self.root_interface.providedBy(location):
                        location = location.aq_parent
                        if location is None:
                            raise RuntimeError("No site found.")

        # Wrap the panel in an acquisition context that provides
        # information about which viewlet manager the panel is
        # implicitly associated with.
        # TODO - name viewlet-manager and panel-manager explicit
        manager = PanelManager(
            self.context, self.request, location, self.normalized_manager_name
        ).__of__(self.context)

        return tuple(manager)
