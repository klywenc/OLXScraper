# Dockerized OLX Scraper Application

This guide explains how to set up and run each component of the OLX Scraper application in separate Docker containers. It also includes documentation on how to interact with the application.

## Redis Docker Setup

### Dockerfile

```dockerfile
FROM redis:latest

EXPOSE 6379
```
### Shell
```shell
docker run --name redis -d -p 6379:6379 redis
```
## RabbitMQ Docker Setup
### Dockerfile
 ```dockerfile
FROM rabbitmq:3-management

EXPOSE 5672 15672
```
### Shell
```shell
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```
### Accessing RabbitMQ Management Dashboard
Navigate to http://localhost:15672 in your web browser.

    Username: guest
    Password: guest

## Webscraper setup

```shell
git clone https://github.com/klywenc/OLXScraper
```
You you don't have to configure anything cuz' everyfile from this repository comes configurated

### Docker setup
```shell
docker compose up --build
```
Everything should work

## Accessing OLX Web Interface

Navigate to http://localhost:8080 in your web browser to access the OLX web interface.
Using the OLX Scraper Application

Enter a keyword to search for and the number of pages to scrape in the OLX web interface.
Click the "Submit" button.
The scraper will start fetching the pages and processing the data. The results will be stored in Redis, and the processing tasks will be handled by RabbitMQ.
You can view the results by navigating to http://localhost:8080/results.
Bug!: Sometimes you need to restart machine it is propably caused by Windows Defender


## Engine Docker Setup

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY engine.py .

CMD ["python", "engine.py"]
```
```shell
docker build -t my-engine-image .
docker run -d --name my-engine-container my-engine-image
```
