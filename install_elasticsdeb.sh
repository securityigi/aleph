#!/bin/bash

echo "Installing JVM..."

#Installation of JVM, requirement of ElasticSearch
apt-get install default-jre -y

echo "Installing ElasticSearch..."

#Adding repositories
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -
echo "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main" >> /etc/apt/sources.list

#Installing ElasticSearch
apt-get update &&  apt-get install elasticsearch -y
update-rc.d elasticsearch defaults 95 10

#Making sure that ElasticSearch is activate
/etc/init.d/elasticsearch start

echo "End of installation."
sleep 1
