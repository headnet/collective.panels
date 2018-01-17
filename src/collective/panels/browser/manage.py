# -*- coding: utf-8 -*-
from zope.interface import implementer_only
from zope.interface import implementer
from zope.component import getMultiAdapter, getUtility
from Products.Five import BrowserView
from plone.registry.interfaces import IRegistry
from collective.panels.interfaces import IManagePanelsView
from collective.panels.interfaces import IManagePanelView
#from plone.app.portlets.browser.manage import ManageContextualPortlets
from collective.panels.interfaces import IGlobalSettings
from zope.component import ComponentLookupError
from Products.statusmessages.interfaces import IStatusMessage
from collective.panels.traversal import PanelManager
from collective.panels import _
from collective.panels.utils import root_interface
from collective.panels.vocabularies import MANAGER_INTERFACE_TO_NAME
from collective.panels.interfaces import IPanelManagerRenderer
from plone.app.portlets.browser.manage import ManageContextualPortlets



@implementer(IManagePanelsView)
class ManagePanels(BrowserView):
    # Inspired by TopbarManagePortlets

    def __init__(self, context, request):
        super(ManagePanels, self).__init__(context, request)
        # Disable the left and right columns
        self.request.set('disable_border', True)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        # Initialize the manager name in case there is nothing
        # in the traversal path
        self.manager_name = 'plone.abovecontentbody'

    def publishTraverse(self, request, name):
        """Get the panel manager via traversal so that we can re-use
        the portlet machinery without overriding it all here.
        """
        self.manager_name = name
        return self

    @property
    def category(self):
        return 'panel'

    @property
    def key(self):
        return '/'.join(self.context.getPhysicalPath())

    def getAssignmentMappingUrl(self, manager):
        # todo
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        return '%s/++panel++%s' % (baseUrl, manager.__name__)

    def render_edit_manager_panels(self):
        manager_view = self
        manager_view.__name__ = 'manage-panels'

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
                if MANAGER_INTERFACE_TO_NAME[interface] == self.manager_name:
                    while not root_interface().providedBy(location):
                        location = location.aq_parent
                        if location is None:
                            raise RuntimeError("No site found.")

        panel_manager = PanelManager(
            self.context, self.request, location, self.manager_name
        ).__of__(self.context)

        panel_manager_renderer = getMultiAdapter((self.context, self.request, manager_view, panel_manager),
                               IPanelManagerRenderer)

        panel_manager_renderer.update()
        return panel_manager_renderer.render()


@implementer(IManagePanelView)
class ManagePanel(ManageContextualPortlets):
    """ Manage view for one panel
    """

    def __init__(self, context, request):
        super(ManagePanel, self).__init__(context, request)

    def getAssignmentMappingUrl(self, manager):
        # This is the panel url - panel is context
        return str(getMultiAdapter((self.context, self.request), name='absolute_url'))

    def getAssignmentsForManager(self, manager):
        assignments = tuple(manager)
        return assignments
