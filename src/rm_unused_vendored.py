#!/usr/bin/env python3
"""Utility to remove unused vendored python used_packages."""

import os
import re
import shutil
import sys

VENDOR_DIR = os.path.expanduser('~/ndotfiles/third_party/pip')


def _main():
  install_scripts = sys.argv[1:]
  script_lines = []
  for script in install_scripts:
    with open(script) as script_file:
      script_lines += script_file.readlines()

  installs = [l for l in script_lines if re.match('pip_install_vendored', l)]
  used_packages = set()
  for install in installs:
    package = re.search('pip_install_vendored ([^ ]+) ', install).groups()[0]
    used_packages.add(package)
  used_packages = set(used_packages)
  vendored_packages = set(os.listdir(VENDOR_DIR))
  unused_packages = vendored_packages - used_packages
  for unused_package in unused_packages:
    package_path = os.path.join(VENDOR_DIR, unused_package)
    print("Removing unused package at %s" % package_path)
    shutil.rmtree(package_path)
  sys.exit(0)


if __name__ == "__main__":
  _main()
