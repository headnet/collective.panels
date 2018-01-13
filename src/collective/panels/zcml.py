from collective.panels.interfaces import ILayout
from zope.component.zcml import handler
from zope.pagetemplate.pagetemplatefile import PageTemplateFile


def panellayout(_context, name, title, description, template, layer):
    component = {
        'name': name,
        'title': title,
        'description': description,
        'template': PageTemplateFile(template),
    }

    adapter = lambda request: component

    _context.action(
        discriminator=('panellayout', name, layer),
        callable=handler,
        args=(
            'registerAdapter',
            adapter, (layer, ), ILayout,
            name, _context.info),
    )
