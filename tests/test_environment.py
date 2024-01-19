
import unittest

from noc_api.services.environment import get_env
from noc_api.exceptions import EnvironmentVarNotExists


class TestEnvironment(unittest.TestCase):
    def test_get_env_exists(self):
        self.assertEqual(get_env("TEST_VAR"), "test value do not remove")

    def test_get_env_not_exists(self):
        with self.assertRaises(EnvironmentVarNotExists):
            get_env("VAR_NOT_PRESENT_IN_THE_ENVIRONMENT")


if __name__ == "__main__":
    unittest.main()
