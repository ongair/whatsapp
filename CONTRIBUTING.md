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


### To be deprecated ###
  ```
    python ongair/run.py -h
    sudo env/bin/python ongair/starter.py -c .env -m 'check'
    sudo env/bin/python ongair/starter.py -c .env -m 'start'
  ```

### Current ###
  ```
    ongair-cli -c .env -a <phone-number>
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


## PyPi Distribution & Releases

### Releases
To maintain the quality and stability of our PIP package we do releases. A release should be best 
done when a couple of features and bugs are checked into the production branch.

### Process of doing a Release
1. Ensure Feature and Hotfix Branches are checked into both develop and master branch.
2. Create a feature/{v1.x.x} branch in preperation for the release.
3. Go to the package and inside go to the __init__.py file and bump up the version number.
4. Close this branch and Publish it by merging it to both develop and master branch.
5. Go to the release section and draft a new release on the Github Page.
6. Write the Tag version in the format v1.X.X and increment till you to 50 e.g 1.1.50 the next should be 1.2.0
7. The Release Title should be also similar to the tag version
8. The description of the release should include the new feature checked in and the new bug fixes.
9. Once done publish the release on Github.
10. Head over to to the terminal and ensure you are on base directory of the repo and also on inside the VirtualEnv.
11. in you bash or zsh create this file ```~/.pypirc``` check the root directory for the template file and add the necessary configs
11. ``` $ python setup.py sdist upload -r pypitest```  To upload it to the test
12. ``` $ python setup.py sdist upload -r pypi``` To upload it to the live pypi


### Notes

* Feature branches automatically branch out of the main develop branch
* Commiting to develop branch directly or the master branch shall not be acceptable
* All work shall be done on it own branch and after done a pull request to be submitted for review.
* You cannot merge your branch to develop, the other developer or technical lead are the only who can merge.
