# Route Optimizer Planner

# Introduction

The goal of this project is to write minimalist route optimizer planner application.

### Main features

* Build an API that takes inputs of start and finish location both within the USA.
* Return a map of the route along with optimal location to fuel up along the route -- optimal mostly means cost effective based on fuel prices
* API to request the route planner service.
* JWT Authentication.
* Load the fixture data for the provided [fuel-prices-for-be-assessment.csv](fuel-prices-for-be-assessment.csv)
* To demonstrate pluggable external map APIs.
* To demonstrate the use of design patterns such as strategy, factory and Singleton.
* Follow SOLID principles.
* Load the fixture in migrate command, scrapped fuel station data along with lat, lon.
* Use pre-commit hook to integrate the hooks to keep code structured.

## Getting Started

First clone the repository from Github and switch to the new directory:

    $ git clone git@github.com/kd17290/route-planner.git
    $ cd route-planner
    
Create and activate the virtualenv for your project.

    source .venv/bin/activate
    
Install project dependencies:
    
    $ pip install -r requirements.txt

Create .env and place the following env variables.
    
    SECRET_KEY=*******************
    MAPQUEST_API_KEY=**********************
    
Then simply apply the migrations:
    Note: this step automatically loads the fixture data scrapped from external map APIs.
    $ python manage.py migrate

Then create superuser
    
    $ python manage.py createsuperuser

You can now run the development server:
    
    $ python manage.py runserver
