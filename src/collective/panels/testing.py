# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.panels


class CollectivePanelsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.panels)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.panels:default')


COLLECTIVE_PANELS_FIXTURE = CollectivePanelsLayer()


COLLECTIVE_PANELS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PANELS_FIXTURE,),
    name='CollectivePanelsLayer:IntegrationTesting'
)


COLLECTIVE_PANELS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PANELS_FIXTURE,),
    name='CollectivePanelsLayer:FunctionalTesting'
)


COLLECTIVE_PANELS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_PANELS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectivePanelsLayer:AcceptanceTesting'
)
