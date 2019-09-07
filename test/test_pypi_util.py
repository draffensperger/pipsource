import unittest
import os
import urllib
import urllib.request
import io

from pipsource import pypi_util


class FakePypiHandler(urllib.request.HTTPHandler):

  def http_open(self, req):
    resp = urllib.addinfourl(
        io.StringIO('{"info":{"home_page":"http://github.com/neovim/python-client"}}'), "mock message", req.get_full_url())
    resp.code = 200
    resp.msg = "OK"
    return resp


class TestPypiUtil(unittest.TestCase):

  def setUp(self):
    opener = urllib.request.build_opener(FakePypiHandler)
    urllib.request.install_opener(opener)

  def tearDown(self):
    urllib._opener = None

  def test_get_git_url_makes_it_https(self):
    self.assertEqual(pypi_util.get_git_url(
        'pynvim'), 'https://github.com/neovim/python-client')

if __name__ == '__main__':
  unittest.main()
