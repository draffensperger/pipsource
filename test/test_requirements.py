import unittest
import os

from pipsource import requirements

class TestRequirements(unittest.TestCase):

    def test_parse(self):
      script_dir = os.path.abspath(os.path.dirname(__file__))
      req_file = os.path.join(script_dir, "fixtures/requirements.txt")

      reqs = requirements.parse(req_file)

      self.assertEqual(reqs, [
        requirements.Requirement(package='pynvim', version='0.3.2'),
        requirements.Requirement(package='autopep8', version='1.4.4'),
        ])

if __name__ == '__main__':
    unittest.main()
