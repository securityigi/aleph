#!/bin/bash

echo "Installing JVM..."

#Installation of JVM, requirement of ElasticSearch
apt-get install default-jre -y

echo "Installing ElasticSearch..."

#Adding repositories
wget -qO - https://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -
sudo add-apt-repository "deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main"

#fix some problems with deb-src ElasticSerach repository
sed -i -e '/deb-src http:\/\/packages.elasticsearch.org\/elasticsearch\/1.4\/debian stable main/d' /etc/apt/sources.list

#Installing ElasticSearch
sudo apt-get update && sudo apt-get install elasticsearch -y
sudo update-rc.d elasticsearch defaults 95 10

#Making sure that ElasticSearch is activate
sudo /etc/init.d/elasticsearch start

echo "End of installation."
sleep 1
