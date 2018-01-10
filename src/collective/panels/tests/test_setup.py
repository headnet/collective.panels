# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.panels.testing import COLLECTIVE_PANELS_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.panels is properly installed."""

    layer = COLLECTIVE_PANELS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.panels is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.panels'))

    def test_browserlayer(self):
        """Test that ICollectivePanelsLayer is registered."""
        from collective.panels.interfaces import (
            ICollectivePanelsLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectivePanelsLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_PANELS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.panels'])

    def test_product_uninstalled(self):
        """Test if collective.panels is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.panels'))

    def test_browserlayer_removed(self):
        """Test that ICollectivePanelsLayer is removed."""
        from collective.panels.interfaces import \
            ICollectivePanelsLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           ICollectivePanelsLayer,
           utils.registered_layers())
