# About

Service that is required to run the OCR Data Preparation App.

# Setup

## Prerequisite

The following softwares need to be installed:

1. Docker
2. Docker Compose

## Building Docker Image

    docker-compose build

The Docker Image only needs to be built once unless a change is made to the service.

## Running the Service

    docker-compose up

The service can be run after the Docker Image has been built. To verify if the service is running correctly, you can use the App that we have released on https://ocr-data-preparation.web.app/.
