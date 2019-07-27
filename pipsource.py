#!/usr/bin/env python3
"""Utility to vendor and install Python pip packages from source."""

import argparse
import logging
import sys
import typing

parser = argparse.ArgumentParser(
    description='Vendor and install pip packages from source.')
parser.add_argument('command', type=str,
                    help="command to run, either 'vendor' or 'install'")
parser.add_argument('requirements_file', type=str,
                    help='the requirements.txt like file to vendor/install')
parser.add_argument('requirements_file', type=str,
                    help='the requirements.txt like file to vendor/install')


class Requirement(typing.NamedTuple):
    package: str
    version: str


def _parse_requirements(requirements_file: str) -> typing.List[Requirement]:
  """Parses out the requirements from a requirements.txt formatted file."""
  with open(requirements_file) as f:
     requirements_lines = f.readlines()

  requirements = []
  for line in requirements_lines:
    if line.startswith('#') or len(line.strip()) == 0:
      continue
    parts = line.split('=')
    if len(parts) != 2:
      logging.error('Malformed requirements line: %s', line)
      sys.exit(1)
    requirements.append(Requirement(package=parts[0], version=parts[1].strip()))
  return requirements


def _run_vendor(requirements: typing.List[Requirement]):
  for r in requirements:
    print(r)


def main():
  """Runs the pipsource command utility."""
  args = parser.parse_args()

  requirements = _parse_requirements(args.requirements_file)

  if args.command == 'vendor':
    _run_vendor(requirements)

if __name__ == "__main__":
  main()
