#!/bin/bash

#Go to /opt/ and execute the command: apt-get install git -y && git clone https://github.com/igorrincon/aleph.git

#Requirements
apt-get install python-pyrex libffi-dev libfuzzy-dev python-dateutil libsqlite3-dev python-pip git -y

#Copy settings file
cp aleph/features/settings.py.orig aleph/features/settings.py

#install ElasticSearch
cd aleph/
chmod +x install_elasticsubnt.sh
./install_elasticsubnt.sh

#Installing and actiate VirtualEnv of python
pip install virtualenv
virtualenv venv
source venv/bin/activate

#Install requirements on VirtualEnv
pip install -r requirements.txt

chmod +x bin/aleph-server.py
./bin/aleph-server.py
