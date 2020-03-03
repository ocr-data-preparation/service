# About

Service to provide resources related to Optical Character Recognition Data Preparation application.

# Development Environment Setup

## Installations

- Install pipenv: `pip install pipenv`.
- Install dependencies: `pipenv install`.

## Environments

Create file to store environment variables, such as `.env`. Some variables already have default value. If you want to configure some variables, please take a look at `config` module for any possible variables to be configured. For simple configuration, define variables below:

```
export PORT=3001
```

## Initial Setup

To use the environment variable when executing command, you can export the environment variable in file named `.env` with command `source ./.env`.

# Run the Program
py
Don't forget to use pip env terminal first. To start the service, use command

> pipenv shell
> python app
