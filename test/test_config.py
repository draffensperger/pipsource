import unittest
import os

from pipsource import config

class TestConfig(unittest.TestCase):

    def setUp(self):
      self.maxDiff = None

    def test_parse(self):
      script_dir = os.path.abspath(os.path.dirname(__file__))
      req_file = os.path.join(script_dir, "fixtures/config.json")

      packages = config.parse(req_file)

      expected_ansicolor = config.Package(
          package='ansicolor',
          git_path='https://github.com/numerodix/ansicolor',
          hg_path=None,
          vendored_version='0.2.6',
          version_commits={
              '0.2.6': 'a5a5c31dc6de5c864a0c5684ae326972573a712b',
          },
          install_requires=[],
          version_tag_format='%s')
      self.assertEqual(packages, {'ansicolor': expected_ansicolor})

if __name__ == '__main__':
    unittest.main()
