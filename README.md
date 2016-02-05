# Setup #

Installing Dependencies

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


On the base repo you will find a file ```.env.template``` and you will need to
run this command to set up the .env

```
   cp .env.template .env
```

You will need then update the `.env` file .



  ```
    python ongair/run.py -h
    sudo env/bin/python ongair/starter.py -c .env -m 'check'
    sudo env/bin/python ongair/starter.py -c .env -m 'start'
  ```




# Contribution Guidelines #

## Developer guidelines

The development process of this project follows the gitflow concept

* master - production
* develop - staging
* feature branches - this will be for any feature you are working
* releases


## Git Flow Setup

### Installation

#### Linux

```
$ apt-get install git-flow
```

#### Mac

```
$ brew install git-flow
```

### Getting Started

1. Initialize your repository with

```
$ git flow init
```

2. Start a new feature

```
$ git flow feature start MYFEATURE
```

3. Work on the feature and then send a PR and tag either of the developers.


4. Merges will be done on the github side rather than the terminal to minimize conflicts.


For more into on git-flow you can read this 2 articles

[ Git Flow CheeatSheet](http://danielkummer.github.io/git-flow-cheatsheet/) . Thanks to Daniel Crammer
[ A successful Git Branching Model](http://nvie.com/posts/a-successful-git-branching-model/) . Thanks to Vincent Driessen

### Notes

* Feature branches automatically branch out of the main develop branch
* Commiting to develop branch directly or the master branch shall not be acceptable
* All work shall be done on it own branch and after done a pull request to be submitted for review.
* You cannot merge your branch to develop, the other developer or technical lead are the only who can merge.