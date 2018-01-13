from zope.interface import implementer_only
from zope.component import getMultiAdapter, getUtility

from collective.panels.interfaces import ITopbarManagePanels
from plone.app.portlets.browser.manage import ManageContextualPortlets


@implementer_only(ITopbarManagePanels)
class TopbarManagePanels(ManageContextualPortlets):

    def __init__(self, context, request):
        super(TopbarManagePanels, self).__init__(context, request)
        # Disable the left and right columns
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        # Initialize the manager name in case there is nothing
        # in the traversal path
        self.manager_name = 'plone-abovecontentbody'

    def publishTraverse(self, request, name):
        """Get the panel manager via traversal so that we can re-use
        the portlet machinery without overriding it all here.
        """
        self.manager_name = name
        return self

    def render_edit_manager_portlets(self):
        # Pay attention again
        # Here we manually render the portlets instead of doing
        # something like provider:${view/manager_name} in the template
        # todo: what view do we get?
        manager_view = ManageContextualPortlets(self.context, self.request)
        manager_view.__name__ = 'manage-panels'
        # todo: the panel manager ?
        portlet_manager = getMultiAdapter(
            (self.context, self.request, manager_view), name=self.manager_name)
        portlet_manager.update()
        return portlet_manager.render()

