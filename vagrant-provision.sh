#!/bin/bash


## During 'vagrant provision' this script runs as root and the current
## directory is '/root'

sudo apt-get update -qq
sudo apt-get autoremove -y
# sudo apt-get upgrade -y
sudo apt-get install -y python-dev python-pip python3 python3.4 python2.7 pypy twine

sudo pip install tox

cd /home/vagrant || exit

# get arrow-keys working in terminal (e.g. editing in vi)
echo 'stty sane' >> ~/.bash_profile
echo 'export TERM=linux' >> ~/.bash_profile

# Kritika (https://github.com/koalaman/shellcheck/wiki/SC1090)
# shellcheck source=/dev/null
source ~/.bash_profile


# other Python versions (optional)
#
# sudo apt-get install -y dpkg-dev zlibc zlib1g zlib1g-dev libssl-dev
#
# wget https://www.python.org/ftp/python/3.2.6/Python-3.2.6.tgz
# tar xzf Python-3.2.6.tgz
# cd Python-3.2.6
# ./configure
# make
# sudo make install
# cd -
#
#
# wget https://www.python.org/ftp/python/3.3.6/Python-3.3.6.tgz
# tar xzf Python-3.3.6.tgz
# cd Python-3.3.6
# ./configure
# make
# sudo make install
# cd -



