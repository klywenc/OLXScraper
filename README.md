# Dockerized OLX Scraper Application
#### By Alan Kalkowski

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

# Documentation

# OLX Scraper Application Documentation

## Python Code Documentation

### Import Statements
- `os`: Used for interacting with the operating system, such as checking file existence and creating directories.
- `datetime`: Provides classes for manipulating dates and times.
- `requests`: Used for making HTTP requests to fetch web pages.
- `lxml.html`: A library for parsing HTML and XML documents.
- `re`: Provides support for regular expressions.
- `collections.Counter`: Used for counting occurrences of elements in a list.
- `asyncio`: Provides infrastructure for writing asynchronous code.
- `concurrent.futures.ProcessPoolExecutor`: Executes tasks in parallel using processes.
- `urllib.parse.urljoin`: Constructs a full URL by combining a base URL and a relative URL.
- `redis`: A Python client for Redis, a key-value store.
- `json`: Used for encoding and decoding JSON data.
- `pika`: A Python RabbitMQ client library.

### Variables
- `redis_db`: Redis database connection object.
- `connection`: RabbitMQ connection object.
- `channel`: RabbitMQ channel object.

### Functions
1. `download_olx_page(page_num, keyword)`: Downloads the HTML page for a given OLX search page number and keyword. **(Asynchronous)**
2. `download_olx_pages(keyword, num_pages=10)`: Downloads multiple OLX search pages for a given keyword. **(Multiprocessing)**
3. `scrape_olx(filename)`: Parses the HTML file and extracts relevant data such as prices and links. **(Synchronous)**
4. `concatenate_and_scrape(keyword, num_pages=10)`: Concatenates downloaded HTML pages and initiates scraping. **(Asynchronous)**
5. `callback(ch, method, properties, body)`: Callback function for processing messages from RabbitMQ queue. **(Asynchronous)**
6. `callback_blocking(ch, method, properties, body)`: Wrapper function to run the callback function asynchronously. **(Asynchronous)**

## Flask Server Documentation

### Features
- **Web Interface**: Provides a user-friendly interface for interacting with the OLX Scraper application.
- **Scraping Form**: Allows users to input a keyword and number of pages to scrape from OLX.
- **Results Page**: Displays the scraped data, including average price, lowest price, and most common price.
- **Asynchronous Communication**: Utilizes AJAX to send requests to the Flask server without reloading the page.

### Endpoints
1. `/`: Renders the main page with the scraping form.
2. `/scrape`: Handles POST requests to initiate the scraping process.
3. `/results`: Renders the results page with the scraped data.

### Dependencies
- **Flask**: A micro web framework for Python.
- **Redis**: An in-memory data structure store, used for caching scraped data.
- **RabbitMQ**: A message broker, used for asynchronous communication between components.

### Usage
- The Flask server coordinates the interaction between the user interface, the Python scraper code, and the Redis cache.
- Users can input search parameters via the web interface, which triggers the scraping process.
- Scraped data is stored in Redis for caching and displayed to the user on the results page.

## JavaScript Code Documentation

### Usage
- The JavaScript code is embedded within HTML files and provides dynamic functionality for interacting with the OLX Scraper application through a web interface.

### Features
- **Interactive Charts**: Dynamically updates charts to visualize price distribution based on user input.

### JavaScript Libraries
- **Chart.js**: Used for creating interactive charts to visualize price distribution.
- **jQuery**: Simplifies DOM manipulation and event handling.
- **Animate.css**: Provides CSS animations for smoother user experience.
#### Variables
- `newest_prices`: An array containing the latest prices, obtained from the Python code.

#### Functions
- `calculateAverage(prices)`: Calculates the average of prices.
- `assignPriceRanges(prices, numBins, minPrice, maxPrice)`: Assigns price ranges and counts for creating a price distribution chart.
- `updateMetric(prices, priceRanges, counts)`: Updates the metrics section with data such as data count, minimum price, maximum price, and average price.
- `updateChart(priceRanges, counts)`: Updates the price distribution chart with new data.
- `updateChartWithCustomRange()`: Updates the chart with custom price range specified by the user.
- Event Listeners:
  - `DOMContentLoaded`: Listens for the DOMContentLoaded event and executes the code inside the callback function once the DOM is fully loaded.
  - `input`: Listens for changes in the bin count input field and updates the chart accordingly.
  - `onClick`: Listens for click events on the chart and logs the clicked label.

## Conclusion
The OLX Scraper application combines Python for backend data processing, Flask for web server functionality, and JavaScript for frontend interactivity, providing users with a seamless web scraping experience.

