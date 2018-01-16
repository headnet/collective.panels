# -*- coding: utf-8 -*-
from zope import schema
from zope.browsermenu.interfaces import IBrowserMenu
from zope.browsermenu.interfaces import IBrowserSubMenuItem
from zope.interface import Attribute
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.container.interfaces import IContained
from collective.panels import _
from zope.configuration.fields import Path
from zope.configuration.fields import GlobalInterface
from zope.contentprovider.interfaces import IContentProvider

#todo: check this:
from plone.app.portlets.interfaces import IColumn


class ICollectivePanelsLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ILayout(Interface):
    """Marker for a layout dictionary."""


class IPanel(IColumn, IContained):
    """A portlet panel.

    Register a portlet for this portlet manager type to enable them
    only for the panel (and not for the regular portlet column
    manager).
    """

    layout = Attribute("Assigned layout.")

    heading = Attribute("Panel heading.")

    css_class = Attribute("Panel css class.")


class IPanelManagerSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the panel manager menu.
    """


class IPanelManagerMenu(IBrowserMenu):
    """The panel manager menu.

    TODO: This gets its menu items from the list of possible portlet managers.
    """


class ITopbarManagePanels(Interface):
    pass


class IManagePanelsView(Interface):
    """Marker for the manage contextual portlets view
    """
    # todo: remove categ.
    category = Attribute("The portlet category being managed")
    key = Attribute("The key in the category under which portlets are assigned")

    def getAssignmentMappingUrl(manager):
        """Given a portlet manager, get the URL to its assignment mapping.
        """

    def getAssignmentsForManager(manager):
        """Get the assignments in the current context for the given manager.
        """


class IPanelManager(Interface):
    """Marker for the manage contextual portlets view
    """


class IPanelManagerRenderer(IContentProvider):
    """A content provider for rendering a panel manager.
    """

    # todo:
    template = Attribute(
        """A page template object to render the manager with.

        If given, this will be passed an option 'portlets' that is a list of
        the IPortletRenderer objects to render.

        If not set, the renderers will simply be called one by one, and their
        output will be concatenated, separated by newlines.
        """)


class IPanelLayoutDirective(Interface):
    name = schema.TextLine(
        title=_("Name"),
        required=True
    )

    title = schema.TextLine(
        title=_("Title"),
        required=True
    )

    description = schema.TextLine(
        title=_("Description"),
        required=True
    )

    template = Path(
        title=_("Template"),
        required=True
    )

    layer = GlobalInterface(
        title=_("Layer"),
        required=True,
        default=ICollectivePanelsLayer,
    )


class IGlobalSettings(Interface):
    site_local_managers = schema.Set(
        title=_(u"Site-local panel managers"),
        description=_(u"The locations listed here will be assignable "
                      u"only at sites (typically Plone's site "
                      u"root, unless local sites are present)."),
        required=False,
        value_type=schema.Choice(
            vocabulary="collective.panels.vocabularies.Managers",
        )
    )

    navigation_local = schema.Bool(
        title=_(u"Use navigation root"),
        description=_(u"Site-local panel managers will be assignable "
                      u"on navigation roots instead of only site roots "
                      u"if you select this option. Check this if you are "
                      u"using LinguaPlone, collective.multilingual or "
                      u"similar, and you want per-language Site-local "
                      u"panel managers."),
    )

