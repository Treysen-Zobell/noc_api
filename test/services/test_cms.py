import unittest

from app.models.exceptions import (
    CmsCommunicationFailure,
    CmsAuthenticationFailure,
    CmsDeauthenticationFailure,
)
from app.services.cms import CmsClient


class TestCmsAuthentication(unittest.TestCase):
    def test_login_wrong_ip(self):
        client = CmsClient()
        client.netconf_url = client.generate_netconf_url(
            "0.0.0.0"
        )  # Change server IP to localhost
        with self.assertRaises(CmsCommunicationFailure):
            client.login()

    def test_login_wrong_username(self):
        client = CmsClient()
        with self.assertRaises(CmsAuthenticationFailure):
            client.login(username="incorrect username")

    def test_login_wrong_password(self):
        client = CmsClient()
        with self.assertRaises(CmsAuthenticationFailure):
            client.login(password="incorrect password")

    def test_invalid_logout(self):
        client = CmsClient()
        with self.assertRaises(CmsDeauthenticationFailure):
            client.logout()

    def test_login_logout(self):
        client = CmsClient()
        client.login()
        client.logout()


class TestCmsOnt(unittest.TestCase):
    pass


class TestCmsModem(unittest.TestCase):
    pass
