# Airport API Service

DRF project written to track and manage flight-related data

## Installation

To set up this project, install PostgresSQL and run these commands:

```shell
git clone https://github.com/o-zinevych/Airport-API.git
cd airport-api
python -m venv venv
venv\Scripts\activate # on Windows
source venv/bin/activate # on macOS
pip install -r requirements.txt
echo "SECRET_KEY=your_secret_key
POSTGRES_DB=airport
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=db
POSTGRES_PORT=5432" > .env
python manage.py migrate
python manage.py runserver # starts Django Server
```

## Running with Docker

Have Docker installed. Then, use these commands:

```shell
docker-compose build
docker-compose up
```

## Getting Access
* Create a user at /api/v1/user/register/
* Create a user with admin permissions
```shell
docker ps # copy airport-db container ID
docker exec -it <container id> sh
python manage.py createsuperuser
```
* Get access token at /api/v1/user/token/

## Features

* User registration, log-in and account management with JWT authentication
* Ability to create and view your ticket orders
* Options for staff to manage and users to browse:
  * airplanes and airplane types available
  * countries, cities and airports open to travel
  * routes and flights
* Filtering flight results by their source, destination and dates
* Staff users have extra functionality to:
  * view and manage the crew working a specific flight
  * upload airport photos for users to see
* Admin panel at /admin/
* Documentation at /api/v1/doc/redoc/ OR /api/v1/doc/swagger/
