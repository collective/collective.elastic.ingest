# Contributor Guidelines

Be human, behave!

# Code-Style

Use `tox -e format` to format the code.
Use `tox -e lint` to check all.


# Development

Create a branch, either in this repo or as a fork, and then create a Pull Request.

# Releases

Are done with the Github release feature.

- Create a draft
- edit version numbers in pyproject.toml and CHANGES.rst and push them
- publish the release:
- Publishing to PyPI and creation of an OCI image is done with GH Actions now.
  Check the Github Actions!
- bump version numbers in above files with `.dev0` postfixed and push, so the repo is back in development mode.
