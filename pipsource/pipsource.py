#!/usr/bin/env python3
"""Utility to vendor and install Python pip packages from source."""

import argparse
import json
import logging
import os
import re
import sys
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
import urllib.request
import config

import pypi_util
import requirements

parser = argparse.ArgumentParser(
    description='Vendor and install pip packages from source.')
parser.add_argument('command', type=str,
                    help="Command to run, either 'vendor' or 'install'")
parser.add_argument('requirements_file', type=str,
                    help='The requirements.txt like file to vendor/install')
parser.add_argument('--config', type=str, default='~/.pipsource/config.json',
                    help='The JSON config file with package source info')
parser.add_argument('--vendor-path', type=str, default='~/.pipsource/vendor/',
                    help='The folder for vendored package sources')

logging.getLogger().setLevel(logging.INFO)


def _get_config(req: requirements.Requirement) -> config.Package:
  git_url = pypi_util.get_git_url(req.package)
  logging.info('got git url: %s', git_url)
  return config.Package(
      package=req.package,
      git_path=git_url,
      hg_path=None,
      vendored_version=req.version,
      install_requires=[],
      version_commits=None)


def _vendor_git_package(package, version, label, git_url):
  label_type, label_value = label
  package_dir = _get_package_dir(package, version)
  git_dir = os.path.join(package_dir, '.git')
  git_moved_dir = os.path.join(package_dir, '.git-moved')
  clone_needed = True

  if os.path.isdir(package_dir):
    subprocess.run(['mv', git_moved_dir, git_dir], stderr=subprocess.DEVNULL)
    if os.path.isdir(os.path.join(package_dir, '.git')):
      if label_type == 'tag':
        tag = subprocess.check_output(
            ['git', 'describe', '--tags', '--exact-match'], cwd=package_dir)
        tag = tag.decode().strip()
        clone_needed = tag != label_value
      elif label_type == 'commit':
        commit = subprocess.check_output(
            ['git', 'rev-parse', '--verify', 'HEAD'], cwd=package_dir)
        commit = commit.decode().strip()
        clone_needed = commit != label_value
      else:
        raise ValueError('Unexpected label type %s' % label_type)

  if clone_needed:
    # Remove the directory contents to make cloning easy (could do a git fetch
    # / checkout but this is simpler and easier).
    subprocess.run(['rm', '-rf', package_dir])
    os.makedirs(package_dir, exist_ok=True)
    git_cmd = ['git', 'clone']
    if label_type == 'tag':
      git_cmd += ['--depth', '1', '--branch', label_value]
    git_cmd += [git_url, package_dir]
    subprocess.run(git_cmd, check=True)
    if label_type == 'commit':
      subprocess.run(
          ['git', 'checkout', label_value], check=True, cwd=package_dir)
  # This makes git think this is just a regular directory so I can check it in,
  # but it preserves the .git folder in another location so I can move it back
  # to check the revision it's at.
  subprocess.run(['mv', git_dir, git_moved_dir], stderr=subprocess.DEVNULL)

def _run_vendor(
    requirements: List[requirements.Requirement],
    configs: Dict[str, config.Package]):
  logging.info('configs: %s', configs)
  for r in requirements:
    if r.package not in configs:
      config = _get_config(r)
      print('got config:')
      print(config)
    print(r)


def main():
  """Runs the pipsource command utility."""
  args = parser.parse_args()

  reqs = requirements.parse(os.path.expanduser(args.requirements_file))
  configs = config.parse(os.path.expanduser(args.config))

  if args.command == 'vendor':
    _run_vendor(reqs, configs)

if __name__ == "__main__":
  main()
