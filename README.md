# pipsource - Install vendored Python pip packages from source

[![circleci][circleci-image]][circleci-url]

This package provides a simple utility for vendoring Python pip packages that are
hosted in git repos and generating a script that will install them into a
virtualenv without relying at all on the PyPI package repository.

See the [Package repo security considerations](https://github.com/draffensperger/dotfiles/blob/master/docs/package-security.md)
for why vendoring, building from source (and code auditing) help protect against
certain types of malicious package attacks.

## Installation

## Usage

Because `pip` packages depend on other packages, in order to vendor a single
package requires vendoring its dependencies.

### 1. Identify the packages you want to vendor and install from source

Create a `requirements.txt` file with those packages. Only exact package
numbers are supported. Example:

```
# requirements.txt
pynvim=0.3.2
autopep8=1.4.4
```

Run `pipsource vendor requirements.txt`

### 2. Vendor the source code for these packages

Run `pipsource`

### 1. Set up a `package_repo_map.json` file

Building those packages from source requires pulling in the source. In order to
do that conveniently, this utility depends on a JSON file that maps pip package
names to their Git (or Mercurial) source URLs and a way to find a commit for a
particular version (via a tag pattern or version to commit map).

See the "JSON package map format" section below for details on the format.

### 2. 




### JSON package map format

You configure a list of desired `pip` packages by creating a JSON file that
looks like this:

```
{
  "packages": [
    "[package-name]": {
      "git": "[git-https-url]",
      "hg": "[mercurial-https-url (use instead of `git` field if package uses hg)]"
      "version-tag-format": "[optional, format with %s, e.g. 'v%s', default is '%s']",
      "version-commits": {
        "[version]": "[git-sha-hash, use this map if package lacks version tags]"
      },
      "skip-vendor-python2": [set to true to not vendor if using python3],
      "skip-vendor-python3": [set to true to not vendor if using python2]
    },
    ...
  ]
}
```

#### Example package map

For example, in this config, `PyYAML` uses the default version tag format of
`%s`, e.g. `5.1.1`. The `ansicolor` package however does not have tags, so we
need an explicit map of version to Git commit hash. The `autoflake` package
shows an exmaple of a non-default version format; it has version tags with a `v`
prefix, e.g. `v1.3`. The `configparser` shows a Mercurial URL example.

```json
{
  "packages": {
    "PyYAML": {
      "git": "https://github.com/yaml/pyyaml"
    },
    "ansicolor": {
      "git": "https://github.com/numerodix/ansicolor",
      "version-commits": {
        "0.2.6": "a5a5c31dc6de5c864a0c5684ae326972573a712b"
      }
    },
    "autoflake": {
      "git": "https://github.com/myint/autoflake",
      "version-tag-format": "v%s"
    },
    "configparser": {
      "hg": "https://bitbucket.org/ambv/configparser"
    }
  }
}
```
[circleci-image]: https://circleci.com/gh/draffensperger/pipsource.svg?style=shield
[circleci-url]: https://circleci.com/gh/draffensperger/pipsource
