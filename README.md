# CS50 Final Project - BREW LOG

#### Live Demo: <https://brewlog.baumert.tech/>

#### Description

A simple web app that allows the user to create an account and log their
brewery experience. This project allowed me to demonstrate an array of
technologies learned including SQL database, API calls, and full-stack
development.

## Overview

This project uses the typical Python / Flask server structure with "app.py"
being the main application file. "app.py" has various functions for login /
logout, brewery search, brewery rating, and confirmation. Most of the
functions require the user to be logged in utilizing a "login_required"
decorator as the app itself is intended to be a user log and not just a general
search. The "templates" folder is typical of a flask project where the
"base.html" file contains the header and footer code for all the pages and is
added using Jinja to the various other pages.

For data storage, I chose to use an SQL relational database with three tables -
User, Brewery, Rating.  This allowed me to store usernames and passwords
separately from a searched breweries. The brewery list is checked when
adding a rank and existing breweries are linked to it to reduce API calls.  
This also makes the website perform faster with local data.

## Features

Utilizing CSS the web app is responsive for both mobile and desktop layouts. On
mobile, I utilized "@media screen" and a custom class to drop certain table
columns to better fit smaller screens.

## Technologies Used

This is a full-stack project utilizing Bootstrap / HTML for the frontend
interface and Python / Flask for the backend server.

### Prerequisites

Python 3.12.0 was installed in VS Codespaces at the time of the project.

### Installation

See "requirements.txt" for needed Python libraries.  Recommend that a virtual
environment is created after which the following command:
```
pip install -r requirements.txt
````
Once the additional libraries have been installed start the server with the
command:
```
flask run
```

## Usage

Starting at the home page the user is asked to log in or register an account.
Once an account is created, the user is then able to search for a brewery and
rate a brewery on beer quality, atmosphere, and location. Afterward, the user
is shown the overall score and given a chance to re-rate or log the entry.

## Roadmap

- DONE: ~~Move away from CS50 library to SQLAlchemy, etc.~~
- DONE: ~~Move to server for hosting to "the world"...~~
- Enable the user to delete or edit a vote
- Institute a "user's choice" for highest rated brewery

## Acknowledgements

The Open Brewery Database for the free dataset and API -
<https://www.openbrewerydb.org/>

## Contact

John Baumert - <baumert.john@gmail.com> - <https://www.johnbaumert.com/>
