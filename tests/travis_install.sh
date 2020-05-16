#!/bin/bash
# This script is meant to be called by the "install" step defined in
# .travis.yml. See http://docs.travis-ci.com/ for more details.
# The behavior of the script is controlled by environment variabled defined
# in the .travis.yml in the top level folder of the project.
#
# This script is inspired by Scikit-Learn (http://scikit-learn.org/)

set -e

pip install -U pip setuptools
pip install tox

if [[ "$COVERAGE" == "true" ]]; then
    pip install -U pytest-cov pytest-virtualenv coverage coveralls flake8 pre-commit
fi


travis-cleanup() {
    printf "Cleaning up environments ... "  # printf avoids new lines
    if [[ "$DISTRIB" == "conda" ]]; then
        # Force the env to be recreated next time, for build consistency
        source deactivate
        conda remove -p ./.venv --all --yes
        rm -rf ./.venv
    fi
    echo "DONE"
}
