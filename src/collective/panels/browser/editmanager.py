# -*- coding: utf-8 -*-
import logging

from plone.memoize.view import memoize

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletManagerRenderer
from plone.portlets.utils import hashPortletInfo

from zope.container import contained
from zope.interface import implementer, Interface
from zope.component import (
    adapts, getMultiAdapter, queryMultiAdapter, getUtility)
from zope.contentprovider.interfaces import UpdateNotCalled
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from five.customerize.zpt import TTWViewTemplateRenderer

from Acquisition import Explicit, aq_parent, aq_inner
from AccessControl import Unauthorized

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote, url_unquote
from Products.CMFCore.utils import getToolByName

from plone.app.portlets.interfaces import IPortletPermissionChecker

from plone.portlets.interfaces import IPortletAssignmentSettings

from collective.panels.interfaces import IPanelManagerRenderer
from collective.panels.interfaces import IManagePanelsView
from collective.panels.interfaces import IPanelManager


@implementer(IPanelManagerRenderer)
class EditPanelManagerRenderer(Explicit):
    """Render a panel manager in edit mode.
    """
    adapts(Interface, IDefaultBrowserLayer, IManagePanelsView, IPanelManager)

    template = ViewPageTemplateFile('templates/edit_panel_manager.pt')

    def __init__(self, context, request, view, manager):
        from ipdb import set_trace; set_trace()
        self.__parent__ = view
        self.manager = manager
        self.context = context
        self.request = request
        self.__updated = False

    @property
    def visible(self):
        # todo: ?
        return True

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        return self.template()

    # Used by the view template

    @property
    def view_name(self):
        # todo
        name = self.__parent__.__name__
        if not name:
            # try to fallback on the 'name' attribute for
            # TTW customized views, see #11409
            if 'TTWView' in self.__parent__.__class__.__name__:
                try:
                    path = self.request.get('PATH_INFO')
                    template_renderer = self.request.traverse(path)
                    name = getattr(template_renderer.template, 'view_name', None)
                except (AttributeError, KeyError, Unauthorized,):
                    logging.getLogger('plone.app.portlets.browser').debug(
                        'Cant get view name for TTV %s' % self.__parent__
                    )
        return name

    def normalized_manager_name(self):
        # for the html 'id'-attribute in the templates
        return self.manager.__name__.replace('.', '-')

    def manager_name(self):
        return self.manager.__name__

    def baseUrl(self):
        return self.__parent__.getAssignmentMappingUrl(self.manager)

    def panels(self):
        assignments = self._lazyLoadAssignments(self.manager)
        return self.panels_for_assignments(
            assignments, self.manager, self.baseUrl())

    def panels_for_assignments(self, assignments, manager, base_url):
        # todo: do we use a special cat for panels?
        category = self.__parent__.category
        key = self.__parent__.key

        data = []
        from ipdb import set_trace; set_trace()
        for idx in range(len(assignments)):
            name = assignments[idx].__name__
            if hasattr(assignments[idx], '__Broken_state__'):
                name = assignments[idx].__Broken_state__['__name__']

            # Todo: we can define an edit view for panels - for overlay etc. - IF needed...
            editview = queryMultiAdapter(
                (assignments[idx], self.request), name='edit', default=None)

            if editview is None:
                editviewName = ''
            else:
                editviewName = '%s/%s/edit' % (base_url, name)

            panel_hash = hashPortletInfo(
                dict(manager=manager.__name__, category=category,
                     key=key, name=name,))

            try:
                # todo: I think we do not have this for panels:
                settings = IPortletAssignmentSettings(assignments[idx])
                visible = settings.get('visible', True)
            except TypeError:
                visible = False

            data.append({
                # todo: a panel has a heading
                'title': assignments[idx].title,
                'editview': editviewName,
                'hash': panel_hash,
                'name': name,
                'up_url': '%s/@@move-portlet-up' % (base_url),
                'down_url': '%s/@@move-portlet-down' % (base_url),
                'delete_url': '%s/@@delete-portlet' % (base_url),
                'hide_url': '%s/@@toggle-visibility' % (base_url),
                'show_url': '%s/@@toggle-visibility' % (base_url),
                'visible': visible,
                })
        if len(data) > 0:
            data[0]['up_url'] = data[-1]['down_url'] = None

        return data

    @memoize
    def referer(self):
        view_name = self.request.get('viewname', None)
        key = self.request.get('key', None)
        base_url = self.request['ACTUAL_URL']

        if view_name:
            base_url = self.context_url() + '/' + view_name

        if key:
            base_url += '?key=%s' % key

        return base_url

    @memoize
    def url_quote_referer(self):
        return url_quote(self.referer())

    @memoize
    def key(self):
        # todo: what is key
        return self.request.get('key', None)

    @memoize
    def _lazyLoadAssignments(self, manager):
        return tuple(manager)

    @memoize
    def context_url(self):
        return str(getMultiAdapter((self.context, self.request), name='absolute_url'))


class ManagePanelAssignments(BrowserView):
    """Utility views for managing panels for a particular panel manager"""

    def authorize(self):
        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u"authenticator")
        if not authenticator.verify():
            raise Unauthorized

    def _render_column(self):
        # todo: what is what here
        view_name = self.request.form.get('viewname')
        obj = aq_inner(self.context.__parent__)
        request = aq_inner(self.request)
        view = getMultiAdapter((obj, request), name=view_name)
        # view can have been customized TTW, see #11409
        if isinstance(view, TTWViewTemplateRenderer):
            view = view._getView()

        manager = getUtility(IPortletManager, name=self.context.__manager__)
        renderer = getMultiAdapter((obj, request, view, manager),
                                   IPortletManagerRenderer)
        renderer.update()
        return renderer.__of__(obj).render()

    def finish_panel_change(self):
        if self.request.form.get('ajax', False):
            return self._render_column()
        else:
            self.request.response.redirect(self._nextUrl())
            return ''

    # view @@move-panel-up
    def move_panel_up(self, name):
        self.authorize()
        assignments = aq_inner(self.context)
        # todo:
        IPortletPermissionChecker(assignments)()

        keys = list(assignments.keys())

        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)
        return self.finish_panel_change()

    # view @@move-panel-down
    def move_panel_down(self, name):
        self.authorize()
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()

        keys = list(assignments.keys())

        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx+1, name)
        assignments.updateOrder(keys)
        return self.finish_panel_change()

    # view @@delete-panel
    def delete_panel(self, name):
        self.authorize()
        assignments = aq_inner(self.context)
        IPortletPermissionChecker(assignments)()

        # set fixing_up to True to let zope.container.contained
        # know that our object doesn't have __name__ and __parent__
        fixing_up = contained.fixing_up
        contained.fixing_up = True

        del assignments[name]

        # revert our fixing_up customization
        contained.fixing_up = fixing_up

        return self.finish_panel_change()

    def _nextUrl(self):
        referer = self.request.get('referer')
        urltool = getToolByName(self.context, 'portal_url')
        if referer:
            referer = url_unquote(referer)

        if not referer or not urltool.isURLInPortal(referer):
            context = aq_parent(aq_inner(self.context))
            url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
            # todo: get the correct fallback referer
            referer = '%s/@@manage-panel' % (url,)
        return referer

    # def toggle_visibility(self, name):
    #     self.authorize()
    #     assignments = aq_inner(self.context)
    #     settings = IPortletAssignmentSettings(assignments[name])
    #     visible = settings.get('visible', True)
    #     settings['visible'] = not visible
    #     return self.finish_panel_change()
