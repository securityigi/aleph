# Aleph - OpenSource Malware Analysis Pipeline System

## What?
Aleph is designed to pipeline the analysis of malware samples. It has a series of collectors that will gather samples from many sources and shove them into the pipeline. The sample manager has a series of plugins that are ran against the sample and returns found data into JSON form.

These JSON data can be further processed and queried in a objective manner instead of *grepping and regexing*.

## How?
The main Aleph daemon is a loose-coupled python application and library. These are composed by the Aleph Service that spawns:

1. The Collectors. These are responsible for going to multiple sources (Filesystem folder, IMAP folder, FTP directory etc) and collect all the files there, store locally and add them to the processing queue. Each collector runs in its own process (fork).
2. Multiple (quantity is configurable) parallel SampleManager services (that will pull samples from the work queue and process them) and run the plugins that receives the sample path and return the JSON object of found artifacts.
3. The sample object is converted to JSON along with its data and is stored into an Elasticsearch backend.

## Installing Aleph

### Requirements
In order to get a clean and nice install, you should download some requirements:

#### Ubuntu

	apt-get install python-pyrex libffi-dev libfuzzy-dev python-dateutil libsqlite3-dev python-pip git -y
	
#### Debian
       
       echo "deb http://ftp.de.debian.org/debian jessie main contrib non-free" >> /etc/apt/sources.list
       apt-get update && apt-get install libfuzzy-dev (**IF NEED TO REBOOT SOME SERVICE, YOU CAN DO IT.**)
       apt-get install python-pyrex libffi-dev python-dateutil libsqlite3-dev python-pip git -y
       
###Preparing your Enviroment

To have a better organization in your enviroment, we will make the installation of Aleph on /opt/ directory.

        cd /opt/
        git clone https://github.com/igorrincon/aleph.git --branch aleph-python --single-branch .
    
Copy the settings file:

        cp aleph/features/settings.py.orig aleph/features/settings.py
	

#### ElasticSearch
First if you don't have an [Elasticsearch](http://www.elasticsearch.org) instance ready, you must install one.

For a easy installation (already with JVM installation), do:

#### Ubuntu
        cd aleph/
        chmod +x install_elasticsubnt.sh
        ./install_elasticsubnt.sh
        
#### Debian
        cd aleph/
        chmod +x install_elasticsdeb.sh
        ./install_elasticsdeb.sh

Or use the installation guide of ElasticSearch for Debian/Ubuntu/Redhat/Fedora/CentOS (yum + apt basically) users, follow [this guide](http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/setup-repositories.html).

** Remember: Elasticsearh uses JVM, so you also must install it =) **

#### Python modules
We strongly suggest that you use python's virtual environment so you don't pollute the rest of your OS installation with python modules. To make a contained virtual environment, install _virtualenv_ with _pip_:
     
    pip install virtualenv

Go to the desired Aleph installation folder and type the following to create and activate your virtual environment:

    virtualenv venv ('venv' can be any name)
    source venv/bin/activate

There will be the environment name (venv) appended to your PS1 variable:

    (venv)(2014-08-19 17:36:%)(~/opt/aleph/)

All python modules required are listed on the _requirements.txt_ file on the root repository folder. You can install all of them at once using _pip_:

    pip install -r requirements.txt

If you wanna change the directory of samples source, edit settings.py and add a local source (a folder where Aleph will search for samples), by default we create the "uploads" directory. - **WARNING: ALEPH WILL MOVE THE SAMPLE THUS REMOVING FROM THE ORIGINAL FOLDER**) _The folder must exists as Aleph won't try to create them_

    SAMPLE_SOURCES = [
        ('local', {'path': '/opt/aleph/uploads'}),
    ]

Review your Elasticsearch installation URI

    ELASTICSEARCH_URI = '127.0.0.1:9200'


#### Running 
With the virtual enviroment already activated, give the execution permission to bin/aleph-server.py and run it as following:

    chmod +x bin/aleph-server.py
    ./bin/aleph-server.py

And that's it. Check your logs under log/aleph.log to any troubleshooting.

#### Install the Web interface(Webui)
Edit the "SERVER_NAME" constant at your settings.py file.
	ex: SERVER_NAME = 'mydomain.com:90'
	
Change the following parameters with you own key (A key that only you know):

	SECRET_KEY = 'Pu7s0m3cryp7l337here' #do not use this ;)

In another terminal window, activate the virtual enviroment:

        cd /opt/aleph
        source venv/bin/activate

Setup your database:

	python bin/db_create.py

Give the execution permission and run the webui script:
	
	chmod +x bin/aleph-webui.sh
	bin/aleph-webui.sh
	
To access your webinterface open your favorite browser at http://SERVER_NAME:5000 #That value you changed before. (By default is http://localhost:5000)
	
	Login: admin
	Password: changeme12!
	
	
**Note: For sake of Security's God, CHANGE YOUR PASSWORD! ;)**
	
But if you do not like our webinterface you still can use other softwares  to review and query data on elasticsearch. I strongly suggest this [Chrome REST client plugin](https://chrome.google.com/webstore/detail/postman-rest-client/fdmmgilgnpjigdojojpjoooidkmcomcm?hl=en) or the great [Kibana](http://www.elasticsearch.org/guide/en/kibana/current/working-with-queries-and-filters.html)

#### Currently implemented
**Collectors**
* FileCollector: grabs samples from a local directory
* MailCollector: grabs samples from email attachments on a IMAP folder

**Plugins**
* PEInfo : extracts info from PE files such as entrypoint, number of sections and some PE characteristics(SEH/ASLR/DEP).
* ZipArchivePlugin: extracts zip files and puts their contents back into analysis queue.
* StringsPlugin: extracts strings from sample into three categories: All Strings, URI Strings and Filename Strings (not 100% but we do our best).
* VirustotalPlugin: check a sample SHA256 hash against Virustotal database and get the report. If that hash doesnt exist, send the file to analise.
* TrID: check the filetype of a sample.
