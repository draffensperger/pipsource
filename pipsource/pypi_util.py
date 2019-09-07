from typing import Optional
import json
import re
import urllib


def get_git_url(package: str) -> Optional[str]:
  """Retrieves GitHub page if specified for given PyPi package via PyPi API."""
  # TODO: make sure this verifies HTTPS certs
  data = urllib.request.urlopen(
      'https://pypi.python.org/pypi/%s/json' % package).read()
  data_parsed = json.loads(data)
  info = data_parsed['info']
  home_page = info.get('home_page')
  if home_page.startswith('http://github.com'):
    home_page = home_page.replace('http://github.com', 'https://github.com')
  if re.match('^https://github.com/', home_page):
    return home_page
  description = info.get('description')
  match = re.search('github.com\/[^\/]+/[a-zA-Z-_]+', description)
  if match:
    return 'https://%s' % match.group(0)
  return None
