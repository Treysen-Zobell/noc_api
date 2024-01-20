import unittest

import pydantic

from app.models.ont import OntGeneral


class TestModel(unittest.TestCase):
    def test_ont_general(self):
        """
        Verifies that 1. Set values exactly match 2. Values are the correct type 3. Values are properly casted 4. Values that cannot be casted raise an error.
        :return:
        """
        ont = OntGeneral(
            parent_node="lab",
            shelf=1,
            registration_id=None,
            low_rx_opt_pwr_ne_thresh=-35.0,
            ont_port_color="0",
        )

        self.assertIsInstance(ont.parent_node, str)
        self.assertIsInstance(ont.shelf, int)
        self.assertIsInstance(ont.low_rx_opt_pwr_ne_thresh, float)
        self.assertIsInstance(ont.ont_port_color, int)

        self.assertEqual(ont.parent_node, "lab")
        self.assertIsNone(ont.registration_id)
        self.assertEqual(ont.shelf, 1)
        self.assertAlmostEqual(ont.low_rx_opt_pwr_ne_thresh, -35.0)

        with self.assertRaises(pydantic.error_wrappers.ValidationError):
            OntGeneral(ont_port_color="nto an int")


if __name__ == "__main__":
    unittest.main()
