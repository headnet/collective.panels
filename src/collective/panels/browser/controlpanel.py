from plone.app.registry.browser import controlpanel
from plone.z3cform import layout
from z3c.form import field

from collective.panels.interfaces import IGlobalSettings
from collective.panels import _


class ControlPanelEditForm(controlpanel.RegistryEditForm):
    id = 'PanelsControlPanel'
    schema = IGlobalSettings
    fields = field.Fields(IGlobalSettings)
    schema_prefix = (
        'collective.panels.interfaces.IGlobalSettings'
    )

    label = _(u"Configure panels")
    description = _(
        u"This form lets you configure the panel add-on product."
    )


ControlPanel = layout.wrap_form(
    ControlPanelEditForm,
    controlpanel.ControlPanelFormWrapper
)
