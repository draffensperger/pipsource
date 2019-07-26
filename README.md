# pip-git-vendor - Utilty for vendoring Python packages from their git repos 

This package provides a simple utility for vendoring Python pip packages that are
hosted in git repos and generating a script that will install them into a
virtualenv without relying at all on the PyPI package repository.

See the [Package repo security considerations](https://github.com/draffensperger/dotfiles/blob/master/docs/package-security.md)
for why vendoring, building from source (and code auditing) help protect against
certain types of malicious package attacks.

## Usage

You configure a list of desired `pip` packages by creating a JSON file that
looks like this:

```json
{
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
  "autopep8": {
    "git": "https://github.com/hhatto/autopep8",
    "version-tag-format": "v%s"
  },
  "backports.functools-lru-cache": {
    "git": "https://github.com/jaraco/backports.functools_lru_cache"
  },
  "chardet": {
    "git": "https://github.com/chardet/chardet"
  },
  "configparser": {
    "hg": "https://bitbucket.org/ambv/configparser"
  },
  "docformatter": {
    "git": "https://github.com/myint/docformatter",
    "version-tag-format": "v%s"
  },
  "enum34": {
    "hg": "https://bitbucket.org/stoneleaf/enum34"
  },
  "flake8": {
    "git": "https://gitlab.com/pycqa/flake8"
  },
  "flake8-docstrings": {
    "git": "https://gitlab.com/pycqa/flake8-docstrings.git",
    "version-commits": {
      "1.3.0": "8245918cca66123c8c5d49438e93d684fcd7a350"
    }
  },
  "flake8-import-order": {
    "git": "https://github.com/PyCQA/flake8-import-order"
  },
  "flake8-polyfill": {
    "git": "https://gitlab.com/pycqa/flake8-polyfill.git"
  },
  "futures": {
    "git": "https://github.com/agronholm/pythonfutures",
    "skip-vendor-python3": true
  },
  "greenlet": {
    "git": "https://github.com/python-greenlet/greenlet"
  },
  "isort": {
    "git": "https://github.com/timothycrosley/isort"
  },
  "lazy-object-proxy": {
    "git": "https://github.com/ionelmc/python-lazy-object-proxy",
    "version-tag-format": "v%s"
  },
  "mccabe": {
    "git": "https://github.com/pycqa/mccabe"
  },
  "msgpack": {
    "git": "https://github.com/msgpack/msgpack-python"
  },
  "neovim": {
    "git": "https://github.com/neovim/python-client"
  },
  "neovim-remote": {
    "git": "https://github.com/mhinz/neovim-remote",
    "version-tag-format": "v%s"
  },
  "pathlib": {
    "hg": "https://bitbucket.org/pitrou/pathlib"
  },
  "pip": {
    "git": "https://github.com/pypa/pip",
    "skip-vendor": true
  },
  "psutil": {
    "git": "https://github.com/giampaolo/psutil",
    "version-tag-format": "release-%s"
  },
  "pycodestyle": {
    "git": "https://github.com/PyCQA/pycodestyle"
  },
  "pydocstyle": {
    "git": "https://github.com/PyCQA/pydocstyle/"
  },
  "pyflakes": {
    "git": "https://github.com/PyCQA/pyflakes"
  },
  "pylint": {
    "git": "https://github.com/PyCQA/pylint",
    "version-tag-format": "pylint-%s"
  },
  "setuptools": {
    "git": "https://github.com/pypa/setuptools",
    "version-tag-format": "v%s"
  },
  "singledispatch": {
    "hg": "https://bitbucket.org/ambv/singledispatch"
  },
  "six": {
    "git": "https://github.com/benjaminp/six"
  },
  "snowballstemmer": {
    "git": "https://github.com/shibukawa/snowball_py",
    "version-commits": {
      "1.2.1": "f7fb6afc03ee6069b79a3eed861019e12d168596"
    }
  },
  "trollius": {
    "git": "https://github.com/haypo/trollius",
    "version-tag-format": "trollius-%s"
  },
  "typing": {
    "git": "https://github.com/python/typing"
  },
  "untokenize": {
    "git": "https://github.com/myint/untokenize",
    "version-tag-format": "v%s"
  },
  "vim-vint": {
    "git": "https://github.com/Kuniwak/vint",
    "version-commits": {
      "0.3.18": "8c34196252b43d7361d0f58cb78cf2d3e4e4fbd0"
    }
  },
  "wheel": {
    "git": "https://github.com/pypa/wheel",
    "skip-vendor": true
  },
  "wrapt": {
    "git": "https://github.com/GrahamDumpleton/wrapt"
  },
  "yapf": {
    "git": "https://github.com/google/yapf",
    "version-tag-format": "v%s"
  }
}
```
