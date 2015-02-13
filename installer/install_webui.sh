#!/bin/bash

#Activating VirtualVenv
cd /opt/aleph
source venv/bin/activate
echo "Please, in another terminal window edit the paramater in features/settings.py know as \"SECRET_KEY\""
read

#Creating Database
python bin/db_create.py

#Installing webui
chmod +x bin/aleph-webui.sh
bin/aleph-webui.sh
