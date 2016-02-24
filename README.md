# ongair-whatsapp

## Introduction

ongair-whatsapp is python package that was built on top of Yoswsup to support Ongair's platform. ongair-whatsapp is 
on top of yowsup layers.


## Requirements

ongair-whatsapp has been tested and known to work on Python27 ; PyPi 4.0


## Installation

I bet you are using [virtualenv](http://www.virtualenv.org/en/latest/index.html) ,right?



At the command line , install ongair-whatsapp using either *pip* (recommended)

```
pip install ongair-whatsapp
```

or *easy_install*

```
easy_install ongair-whatsapp
```

## Project Structure

``` bash
├── CONTRIBUTING.md
├── LICENCE
├── MANIFEST.in
├── README.md
├── dist
│   └── ongair-whatsapp-1.0.0.tar.gz
├── logs
├── ongair
│   ├── __init__.py
│   ├── client.py
│   ├── models.py
│   ├── notification.py
│   ├── ongair-example.conf
│   ├── ongair.py
│   ├── stack.py
│   ├── starter.py
│   ├── util.py
├── ongair-cli
├── ongair_whatsapp.egg-info
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── requires.txt
│   └── top_level.txt
├── requirements.txt
├── setup.cfg
├── setup.py
└── tmp
```



## Scripts

ongair-whatsapp comes with a launch script ``` ongair-cli ```

## Setup
 
```pip install -r requirements.txt```

## Credits

Shoutouts to Yowsup for inspriting ongair-whatsapp

## Licence

ongair-whatsapp is distributed under the GPL V3 Licence