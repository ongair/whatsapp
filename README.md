## Setup ##
Installation

  ```
    sudo apt-get update
    sudo apt-get install python-pip
    
    sudo apt-get install libmysqlclient-dev python-dev #python-dev only for ubuntu
    # for ubuntu
    sudo apt-get install libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev
    
    sudo pip install virtualenv
    virtualenv env

    source env/bin/activate
    
    pip install -r requirements.txt
  ```

## Running ##

  ```
    python ongair/run.py -h
    sudo env/bin/python ongair/starter.py -c .env -m 'check'
    sudo env/bin/python ongair/starter.py -c .env -m 'start'
  ```
  