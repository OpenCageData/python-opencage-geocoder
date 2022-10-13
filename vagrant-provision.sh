#!/bin/bash

sudo apt-get update -qq
sudo apt-get install --no-install-recommends -q -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# https://github.com/pyenv/pyenv-installer#readme
curl -s -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash


echo '
export PATH="${HOME}/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
' >> ~/.bashrc
source ~/.bashrc
exec $SHELL

for VERSION in 3.6.13  3.7.10  3.8.15  3.9.2  3.10.8; do
  echo "Installing $VERSION ..."
  pyenv install --skip-existing $VERSION
  pyenv global $VERSION
done

sudo apt-get install -y python3-pip
# Python 3.8 has conflicts with upstream Ubuntu and removed distutils from base
# installation, now add a global one back
sudo apt-get install --no-install-recommends -q -y python3-distutils

pyenv versions

sudo pip3 install tox
