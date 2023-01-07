#!/bin/bash

sudo apt-get update -qq
sudo apt-get install --no-install-recommends -qq -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

export PATH="${HOME}/.local/bin:$PATH"

# pip and tox should be installed with system python, not any .pyenv environments
sudo apt-get install -y python3-pip
pip install --upgrade pip
pip install tox


# https://github.com/pyenv/pyenv-installer#readme
curl -s -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash


echo '
export PATH="${HOME}/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
' >> ~/.bashrc
source ~/.bashrc
exec $SHELL

# 'exec $SHELL' doesn't work well in a provision file. Likely you need to
# run the following commands manually after 'vagrant up'

for VERSION in 3.7 3.8 3.9 3.10 3.11; do
  VERSION=$(pyenv latest --known $VERSION)
  echo "Installing $VERSION ..."
  pyenv install --skip-existing $VERSION
done

# Any version not part of the globals isn't found by tox' envlist
pyenv global $(pyenv versions --bare)
pyenv versions
