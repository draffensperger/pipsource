import logging
import os
import json

from typing import Optional
from typing import Dict
from typing import NamedTuple
from typing import List

DEFAULT_VERSION_TAG_FORMAT = '%s'

class Package(NamedTuple):
    package: str
    git_path: Optional[str]
    hg_path: Optional[str]
    vendored_version: Optional[str]
    version_commits: Optional[Dict[str, str]]
    install_requires: List[str]
    version_tag_format: str


def parse(config_file: str) -> Dict[str, Package]:
  """Loads package map from JSON file."""
  if not os.path.isfile(config_file):
    logging.info('Config file %s does not exist yet' % config_file)
    return {}

  with open(config_file) as f:
    config_json = json.loads(f.read())

  if 'packages' not in config_json:
    logging.critical('Config JSON must have "packages" field')
    sys.exit(1)
  packages = config_json['packages']
  if not type(packages) is dict:
    logging.critical('Config JSON "packages" field must be an object')
    sys.exit(1)

  parsed_packages = {}
  for package in packages:
    package_json = packages[package]
    parsed_packages[package] = Package(
        package=package,
        git_path=package_json.get('git'),
        hg_path=package_json.get('hg'),
        vendored_version=package_json.get('vendored'),
        version_tag_format=(
            package_json.get('version-tag-format', DEFAULT_VERSION_TAG_FORMAT)),
        version_commits=package_json.get('version-commits'),
        install_requires=package_json.get('install_requires', []))
  return parsed_packages
