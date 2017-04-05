# What is mccelections?

mccelections is a Django application that can be used for any of the following election result-related tasks:

* ingesting AP election results using the [Elex API wrapper](https://github.com/newsdev/elex)
* ingesting results that have been hand-keyed or scraped into a Google Sheet (Google Sheets can parse HTML, XML and other structured data formats simply by setting up the proper formula)
* writing custom Python scrapers to ingest results data
* hand-keying results data directly into the Django admin
* automatically calculating vote percent and precinct reporting percents for hand-keyed, Google Sheet or scraped results
* recording and replaying results data, such as from AP tests
* automatically simulating manual data changes
* storing AP, scraped, manual or any combination of data in a unified format
* outputting this data as a RESTful API

# Setting up and running mccelections

Thanks to
* Digital Ocean's [How To Serve Django Applications with uWSGI and Nginx on Ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-ubuntu-14-04)
* @panuta's [How to setup Django server with virtualenv on Ubuntu Server 12.04](https://gist.github.com/panuta/3075882); for reference, [here's my fork of that](https://gist.github.com/greglinch/2b03e87ecc8d84790cc7)
* @jeremybowers all of his advice along the way.

## Initial requirements

* Python 2.7.x
* OS X or Ubuntu 14
* Homebrew

## Optional requirements

* Associated Press API key (for ingestion)
* Amazon S3 bucket (for baking to static)    

If you're using an S3 bucket, then you need to add these to your `.bash_profile` (Mac) or `.bashrc` (Ubuntu) file with their respective values:

     S3_ACCESS_KEY=''
     S3_SECRET_KEY=''
     S3_BUCKET=''

## Get your local environment ready

Install pip

    easy_install pip

Install virtualenv

    pip install virtualenv virtualenvwrapper

Install postgresql

    brew install postgresql

# Get your server environment ready
I recommend setting up both `test` and `prod` environments.

### Connect to server via ssh

If using a pem key with AWS

    ssh -i <filepath>/<filename>.pem <username>@<host.com>

If whitelisted via AWS, then

    ssh <username>@<host.com>

### Install necessary packages

Check for package updates

    sudo apt-get update

Upgrade those packages

    sudo apt-get upgrade

Install Python dependencies

    sudo apt-get install python-pip python-dev python-setuptools

Install virtualenv and virtualenvwrapper

    sudo pip install virtualenv virtualenvwrapper

Install postgres

    sudo apt-get install postgresql python-psycopg2 libpq-dev

If you just need the postgres client (e.g. connecting to database via Amazon RDS), then try this ([h/t Postgres docs](https://help.ubuntu.com/community/PostgreSQL))

    sudo apt-get install postgresql-client

### Install Slack integration packages (optional)

For Slackbot, if you want to avoid SSL warnings, [via this SO thread](https://stackoverflow.com/questions/29134512/insecureplatformwarning-a-true-sslcontext-object-is-not-available-this-prevent):

    sudo apt-get install libffi-dev libssl-dev

These are included in `requirements.txt`, so you can remove them if you're not using the Slackbot

    pip install pyopenssl ndg-httpsclient pyasn1

##  Set up the Django app (local or server)

### Prep for using AP API (optional)

Add the following to your `.bash_profile` for a Mac or `.bashrc` for Ubuntu:

AP API key

    echo "export AP_API_KEY=<API_KEY_HERE>" >> ~/.bash_profile

Elex recording type

    echo "export ELEX_RECORDING=flat" >> ~/.bash_profile

Elex recording directory

    echo "export ELEX_RECORDING_DIR=/tmp/ap-elex-data/" >> ~/.bash_profile

Feel free to change this path based on your particular preference or server set up. Just  be sure all other paths below (search for `/home/ubuntu/`) reflect where your project lives.

    echo "export SAVER_DIR=/home/ubuntu/mccelections/electionsproject/snapshots" >> ~/.bash_profile

Create an Elex recording directory, for example

    mkdir -p /tmp/ap-elex-data/

### Set up virtualenv and virtualenvwrapper

Create the environments directory, if you don't have one already. You can name this anything you like, as long as it's consistent with future related steps.

    mkdir -p ~/Envs

Set the workon home, which is a shortcut with virtualenvwrapper (`.bash_profile` for Mac, `.bashrc` for Ubuntu)

    echo "export WORKON_HOME=~/Envs" >> ~/.bash_profile

Source the virtualenvwrapper file

    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bash_profile

Source your bash profile for the changes to take effect in that terminal tab

    source ~/.bash_profile

### Install git

On Ubuntu

    sudo apt-get install git

On OS X, follow these instructions

    https://git-scm.com/book/en/v2/Getting-Started-Installing-Git#_installing_on_mac

### Generate an ssh key for GitHub

Execute this command in your terminal

    ssh-keygen -t rsa -b 4096 -C "<YOUR_EMAIL_ADDRESS>"

Enter this as the file, for example

    /home/ubuntu/.ssh/id_rsa

Enter a secret passphrase

On Mac, copy it to clipboard with

    pbcopy < ~/.ssh/id_rsa.pub

On other platforms like Ubuntu, you can use a text editor like vim to read and copy the file contents

    vim ~/.ssh/id_rsa.pub

Or run this to output it to the terminal

    cat ~/.ssh/id_rsa.pub

Then highlight, copy and paste it as a new SSH key in GitHub

### Clone GitHub repo

Make sure you're in the correct directory, such as root

    cd ~

Clone the repo

    git clone git@github.com:mcclatchy/mccelections.git

Change into that directory

    cd ~/mccelections

### Make your virtualenv

Using a handy command that comes with virtualenvwrapper

    mkvirtualenv mccelections

### Install requirements

This will install all the Python packages used by `mccelections`. If you don't plan to use certain features (e.g. Slack integration), feel free to remove them before installing.

    pip install -r requirements.txt

### Django setup

Create a private settings file for each environment. *NOTE:* These files are excluded from version control in the `.gitignore` file, but it's important to confirm before comittting.

    touch ~/mccelections/electionsproject/electionsproject/settings_private.py

Add the following settings to each environment's file with the correct values in place of the `<VALUE>` listed for each variable:

     SECRET_KEY = "<SECRET_KEY>"

     ## Slack token to send messages to related account
     SLACK_TOKEN = "<SLACK_TOKEN>"

     ## TEST
     db_engine = "django.db.backends.postgresql_psycopg2"
     db_name = "<NAME>"
     db_user = "<USER>"
     db_password = "<PASSWORD>"
     db_host = "<HOST>"
     db_port = "<PORT>"

In `settings_test.py` and `settings_prod.py`, you must add the related domains for the API base URL

     MCC_API_BASE_URL

And Django allowed hosts

     ALLOWED_HOSTS

If you're using a server, copy the server-specific settings to main settings file

    cp electionsproject/settings_test.py electionsproject/settings.py

or

    cp electionsproject/settings_prod.py electionsproject/settings.py

If you're using localhost, make sure the database settings are correct. If you haven't already created a postgres database and user, you need to do that. For example, on a Mac

     https://updatemycode.com/2016/11/23/installing-postgresql-on-mac-os-x/

Check the settings file and verify everything is correct

Make sure you're in the app directory before running any management command, such as the initial database migration

    cd ~/mccelections/electionsproject/results

Then migrate the database

    ./manage.py migrate

Now create a Django superuser

    ./manage.py createsuperuser

Collect static files

    ./manage.py collectstatic

Enter 'yes' to overwrite

### Make sure all shell scripts have perms to run (optional)

Only necessary if you plan to use the bash scripts

    chmod u+x bashscripts/*

## Running the localhost server

### setup for local

If you're on localhost, start the Django development server

    ./manage.py runserver

Make sure you see this

     Django version 1.9, using settings 'elections.settings'
     Starting development server at http://127.0.0.1:8000/

## Running the remote server

### uWSGI setup

If you're on an Ubuntu server, you'll need to install and configure the server

    sudo pip install uwsgi
    sudo mkdir -p /etc/uwsgi/sites
    cd /etc/uwsgi/sites

### ini file

    sudo vim electionsproject.ini

Update your virtualenv name below for `<YOUR_ENV>` and then paste this block

     [uwsgi]
     project = electionsproject
     base = /home/ubuntu/mccelections/electionsproject

     chdir = %(base)/%(project)
     home = /home/ubuntu/Envs/<YOUR ENV>
     module = %(project).wsgi:application

     master = true
     processes = 5

     socket = %(base)/%(project)/%(project).sock
     chmod-socket = 664
     vacuum = true

Save and close

### Upstart script

Edit the uwsgi configuration

    sudo vim /etc/init/uwsgi.conf

Add the following

     description "uWSGI application server in Emperor mode"

     start on runlevel [2345]
     stop on runlevel [!2345]

     setuid ubuntu
     setgid www-data

     exec /usr/local/bin/uwsgi --emperor /etc/uwsgi/sites

Save and close

## nginx setup

Install nginx

    sudo apt-get install nginx

Edit the configuration

    sudo vim /etc/nginx/sites-available/electionsproject

Paste the following and be sure to replace `<hostname>` with your host. If you want all domains to be able to access the API data (a.k.a. CORS, cross-orgin requests), use `'*'` there -- as it is currently. If you want to specify a domain, add it there instead. You can also update the cache expiration time as desired.

     server {
        listen 80;
        server_name <hostname>;
        access_log /var/log/nginx/electionsproject_access.log;
        error_log /var/log/nginx/electionsproject_error.log;

        location = /favicon.ico { access_log off; log_not_found off; }

        location /static/ {
            root /home/ubuntu/mccelections/electionsproject;
        }

        location / {
            add_header      'Access-Control-Allow-Origin' '*';
            add_header       Cache-Control "public";
            expires          1h;
            include          uwsgi_params;
            uwsgi_pass       unix:/home/ubuntu/mccelections/electionsproject/electionsproject.sock;
        }

        location /admin {
             include          uwsgi_params;
             uwsgi_pass       unix:/home/ubuntu/mccelections/electionsproject/electionsproject.sock;
        }

        location /api/v1/resultlive {
            add_header       'Access-Control-Allow-Origin' '*';
            add_header       Cache-Control "public";
            expires          1m;
            include          uwsgi_params;
            uwsgi_pass       unix:/home/ubuntu/mccelections/electionsproject/electionsproject.sock;
        }

        location /v1/resultlive {
            add_header       'Access-Control-Allow-Origin' '*';
            add_header       Cache-Control "public";
            expires          1m;
            include          uwsgi_params;
            uwsgi_pass       unix:/home/ubuntu/mccelections/electionsproject/electionsproject.sock;
        }

        location /api/v1/resultmanual {
          add_header       'Access-Control-Allow-Origin' '*';
          add_header       Cache-Control "public";
          expires          1m;
          include          uwsgi_params;
          uwsgi_pass       unix:/home/ubuntu/mccelections/electionsproject/electionsproject.sock;
        }

        location /v1/resultmanual {
          add_header       'Access-Control-Allow-Origin' '*';
          add_header       Cache-Control "public";
          expires          1m;
          include          uwsgi_params;
          uwsgi_pass       unix:/home/ubuntu/mccelections/electionsproject/electionsproject.sock;
        }

     }

## Finish remote server setup

Create a symlink for the nginx configuration

    sudo ln -s /etc/nginx/sites-available/electionsproject /etc/nginx/sites-enabled

Make sure the symlink worked

    ll /etc/nginx/sites-enabled/

Check the configuration (make sure it says "OK" and doesn't throw any errors)

    sudo service nginx configtest

Restart nginx

    sudo service nginx restart

Start uwsgi

    sudo service uwsgi start

Or, if uwsgi was already running

    sudo service uwsgi restart

### Django app changes not appearing?

If you've made a model or admin change, ran the migration and still aren't seeing the change reflected in the admin on a server, you can try runnning restarting uwsgi. If you still aren't seeing the change, try rebooting the server.

    sudo reboot

Check the url

    domain.com/admin

## Making future work easier

On a server, log in

    ssh <username>@<host.com>

On a local machine, open your terminal application

Activate the virtualenv and change to that directory

    workon mccelections && cd code/mccelections/electionsproject/

You can also set up an alias for this in your `.bash_profile` (Mac) or `.bashrc` (Ubunutu)

    echo "alias mccelections='workon mccelections && cd code/mccelections/electionsproject/'" >> ~/.bash_profile

Then to have it take effect
    
    source ~/.bash_profile

Test by running this

    mccelections

## Workflow to update your servers

If you're not pushing any changes back to the repo, checkout any edited files to remove the updates

    git checkout -- .

Grab the latest files off of GitHub, such as from the master branch. If you're on the test server and want to pull a test branch, specific that branch instead.

    git pull origin master

Enter your secret passphrase

Make migrations based on the new changes (because migrations are listed in `gitignore`)

     ./manage.py makemigrations

Migrate the database

     ./manage.py migrate

## How to use the app

You should be all set to start add or ingesting data! To test the main URLs:

* `/admin` - add/update/delete data
* `/api/v1/<model>/?format=json` - API url pattern

For more information on how to use the app as a developer, visit the [developer instructions](https://github.com/mcclatchy/mccelections/wiki/Developer-instructions).

Questions? Suggestions? Submit a pull request or contact: greglinch [at] gmail [dot] com
