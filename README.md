# Esusu

A corporative society app that allows users to save a fixed amount automatically every week, with the money collected by one of the members at the end of each month.

## API Documentation

The API for this app is documented here: https://bit.ly/esusu-docs

## Getting Started

These instructions will get a local copy of the project up and running for development and testing purposes.

### Prerequisites

- Git
- Python (3+)
- Postgres
- A Paystack Account

### Installation

- Clone repo `https://github.com/danielcoker/esusu.git`
- Change into the directory of the project.
- Run `cp .env.example .env` to create a copy of the environment variables.
- Fill in the details of the environment varibles.
- Run `pipenv install` to install required packages.
- Run `pipenv shell` to activate the virtual env.
- Run `python manage.py migrate` to run migrate.
- Run `python manage.py runserver` to start the development server.

> Create a secret key for the Django app here: https://djecrety.ir/

### Testing

The applicaton uses `pytest` for testing.

Run `pytest` to execute tests. <br>You can also add `--cov` to get test coverage report along with the test results.

## Features

- Users can create an account (register/login).
- Users can create a savings group.
- Users can search for public groups to join.
- Users can join groups.
- Users can see a list of members in their group.
- Users can view the savings and payment list of their group.
- Users can add their bank and card details (for savings and receiving payments).

- The app has endpoints for initiating savings and payments due for a particular day across the app. (These services can be moved into a scheduler.)

## Technologies and Services

- Django REST Framework
- Posgres
- Paystack

## Contributing

To contribute to this project:

- Fork the repository.
- Create a new branch for your contribution.
- Raise a pull request against the `main` branch.

## Author

Daniel Coker (https://twitter.com/danielcoker_)

## Licence

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
