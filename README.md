# Airport API Service

This DRF project can be used to track and manage flight-related data all over the world.

## Installation

To set up this project, run these commands:

```shell
git clone https://github.com/o-zinevych/Airport-API.git
cd airport-api
python -m venv venv
venv\Scripts\activate # on Windows
source venv/bin/activate # on macOS
pip install -r requirements.txt
python manage.py runserver # starts Django Server
```

## Features

* Functionality allowing users to register, log in and manage their accounts securely
* Ability to place and view your ticket orders
* Options for staff to manage and users to browse:
  * airplanes and airplane types available
  * countries, cities and airports open to travel
  * routes and flights
* Users may also filter flight results by their source, destination and dates
* Staff users have extra functionality to:
  * view and manage the crew working a specific flight
  * upload airport photos for users to see
