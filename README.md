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

