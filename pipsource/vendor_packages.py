#!/usr/bin/env python3
"""Utility to vendor Python packages from GitHub."""

# TODO: better heuristics
# Common issues I had importing packages were:
# - version tags are often either "v%s" or "package-%s" formatted, and those
#   could be auto-detected.
# - some packages don't use tags at all. We should check if the HEAD of the
#   master branch happens to be the version we are looking for, if so,
#   add a commit for that to the version commit map
# - would be nice to be able to auto-detect bitbucket hg repos.

import json
import os
import re
import stat
import subprocess
import sys
from urllib import request

PACKAGE_MAP_FILE = (
    os.path.expanduser('~/ndotfiles/install/third_party/pip/package_map.json'))

PIP_VENDOR_DIR = os.path.expanduser('~/ndotfiles/third_party/pip/')

INSTALL_SCRIPT_NAME = 'install_venv_vendored.sh'


def _load_package_map():
  """Loads package map from JSON file."""
  with open(PACKAGE_MAP_FILE) as package_map_file:
    return json.loads(package_map_file.read())


def _save_package_map(package_map):
  with open(PACKAGE_MAP_FILE, 'w') as package_map_file:
    json.dump(package_map, package_map_file, sort_keys=True, indent=2)


def _get_git_url(package):
  """Retrieves GitHub page if specified for given PyPi package via PyPi API."""
  data = request.urlopen(
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


def _should_vendor(package, package_map, python_bin):
  package_info = package_map.get(package)
  if not package_info:
    return True
  if python_bin == 'python3' and package_info.get('skip-vendor-python3'):
    return False
  return not package_info.get('skip-vendor')


def _get_packages_and_versions(graph, package_map, python_bin):
  """Gets list of packages given `pipenv graph --reverse --bare` string.

  It returns them such that packages with dependencies are listed after the
  packages that depend on them.
  """
  lines = graph.split('\n')
  packages = set()
  max_depths = {}
  for line in lines:
    if not line:
      continue
    package_match = re.search('(\s*)-?\s*([^=]+)==(\d+\.\d+(?:\.\d+)*)', line)
    whitespace, package, version = package_match.groups()
    depth = len(whitespace) / 2
    max_depths[package] = max(depth, max_depths.get(package, 0))
    packages.add((package, version))
  # Sort by max depth then by package name
  packages = sorted(list(packages), key=lambda p: (max_depths[p[0]], p[0]))
  packages = [
      p for p in packages if _should_vendor(p[0], package_map, python_bin)
  ]
  return packages


def _add_packages_to_map(packages, package_map):
  """Tries to find given packages' git paths and adds to package_map."""
  found_all = True
  for package in packages:
    if package in package_map:
      continue
    git_page = _get_git_url(package)
    if git_page:
      package_map[package] = {'git': git_page}
    else:
      print("Git page not found for package: %s" % package)
      found_all = False
  return found_all


def _get_package_dir(package, version):
  # I used to use "os.path.join(PIP_VENDOR_DIR, package, version)" in case I
  # would need more than one version of a particular package at a given time,
  # but I later decided that I would try to avoid that to simplify the process
  # of reviewing updates to packages.
  del version  # Unused
  return os.path.join(PIP_VENDOR_DIR, package)


def _vendor_hg_package(package, version, label, hg_url):
  label_type, label_value = label
  if label_type != 'tag':
    raise ValueError('hg vendoring expects a tag')
  hg_tag = label_value
  package_dir = _get_package_dir(package, version)
  if (os.path.isdir(package_dir) and
      os.path.isdir(os.path.join(package_dir, '.hg'))):
    tag = subprocess.check_output(
        ['hg', 'log', '-r', '.', '--template', '{latesttag}'], cwd=package_dir)
    tag = tag.decode().strip()
    if tag == hg_tag:
      return
    setup_py_version = subprocess.check_output(
        ['python', 'setup.py', '--version'], cwd=package_dir)
    setup_py_version = setup_py_version.decode().strip()
    if setup_py_version == version:
      return
  subprocess.run(['rm', '-rf', package_dir])
  hg_cmd = ['hg', 'clone', '-r', hg_tag, hg_url, package_dir]
  subprocess.run(hg_cmd, check=True)


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


def _get_version_label(package, version, package_info):
  if 'version-tag-format' in package_info:
    version_tag_format = package_info['version-tag-format']
    return ('tag', version_tag_format % version)
  elif 'version-tags' in package_info:
    version_tags = package_info['version-tags']
    return ('tag', version_tags.get(version, version))
  elif 'version-commits' in package_info:
    version_commits = package_info['version-commits']
    return ('commit', version_commits[version])
  return ('tag', version)


def _vendor_package(package, version, package_info):
  print("Vendoring %s version %s" % (package, version))
  label = _get_version_label(package, version, package_info)
  git_url = package_info.get('git')
  if git_url:
    _vendor_git_package(package, version, label, git_url)
    return
  hg_url = package_info.get('hg')
  if hg_url:
    _vendor_hg_package(package, version, label, hg_url)
    return
  print("No hg or git URL for package %s" % package)
  sys.exit(1)


def _vendor_packages(packages_and_versions, package_map):
  for package, version in packages_and_versions:
    package_info = package_map[package]
    _vendor_package(package, version, package_info)


def _get_install_line(package, version):
  package_dir = _get_package_dir(package, version)
  need_git_tag = False
  try:
    print("Checking if git version tag needed for %s" % package)
    subprocess.run(
        ['python', 'setup.py', '--version'],
        cwd=package_dir,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
  except subprocess.CalledProcessError:
    need_git_tag = True
  line = 'pip_install_vendored %s "%s"' % (package, version)
  if need_git_tag:
    line += ' git_version_tag'
  return line


def _write_install_script(packages_and_versions, pipenv_dir, python_bin):
  script_lines = [
      '#!/usr/bin/env bash',
      'set -e',
      'source ~/ndotfiles/scripts/venv_vendor_util.sh',
      'virtualenv --no-download .venv-vendored --python=$(which %s)' %
      python_bin,
      'source .venv-vendored/bin/activate',
  ]
  for package, version in packages_and_versions:
    script_lines.append(_get_install_line(package, version))
  script_lines.append('deactivate')
  script_path = os.path.join(pipenv_dir, INSTALL_SCRIPT_NAME)
  with open(script_path, 'w') as script_file:
    script_file.write('\n'.join(script_lines))
  script_stat = os.stat(script_path)
  os.chmod(script_path, script_stat.st_mode | stat.S_IEXEC)
  print('Wrote install script %s' % script_path)


def main():
  """Runs the vendor utility."""
  pipenv_dir = sys.argv[1]
  if len(sys.argv) > 2:
    python_bin = sys.argv[2]
  else:
    python_bin = 'python'

  # Do a pipenv install first if needed.
  if not os.path.isdir(os.path.join(pipenv_dir, '.venv')):
    pipenv_env = os.environ.copy()
    pipenv_env['PIPENV_VENV_IN_PROJECT'] = '1'
    subprocess.run(
        ['pipenv', 'install', '--ignore-pipfile'],
        cwd=pipenv_dir,
        env=pipenv_env)

  package_map = _load_package_map()

  graph = subprocess.check_output(
      ['pipenv', 'graph', '--reverse', '--bare'], cwd=pipenv_dir)
  graph = graph.decode()
  packages_and_versions = _get_packages_and_versions(graph, package_map,
                                                     python_bin)
  packages = [p[0] for p in packages_and_versions]
  all_packages_in_map = _add_packages_to_map(packages, package_map)
  _save_package_map(package_map)
  if not all_packages_in_map:
    print("Could not find git links for all packages in graph")
    sys.exit(1)

  _vendor_packages(packages_and_versions, package_map)
  _write_install_script(packages_and_versions, pipenv_dir, python_bin)

  sys.exit(0)


if __name__ == "__main__":
  main()
