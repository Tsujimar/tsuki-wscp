## tsuki-wscp
tsuki-wscp is a web scraper that provides data collection for AI model training
## Supported sources (more to come)
- 4Chan
- Reddit
## What to expect
![average rows a sec](https://i.gyazo.com/06451df4560e2bab153d61f1efd4dae5.png)
- Apx 100-130 data rows a second
- Constant 20-30% cpu usage
- 10-20 Mbps network usage
## Usage
```python3 tsuki-wscp [-s {1-5}] [--nsfw-toggle]```
- The ```-s``` option is used to specify the driver delay. The value should be between 1 and 5. A higher delay can help prevent your IP from being blocked by the website.
- The ```--nsfw-toggle``` option enables scraping of highly NSFW boards. Note that this option should only be used if you are of legal age and comfortable with such content. 
- Please keep in mind that even the default boards WILL HAVE nsfw content but not as much.

Before running the script make sure you set the environment variables
- export DB_NAME=your_database_name
- export PG_USER=your_postgres_user
- export PG_PASSWORD=your_postgres_password
- export PG_PORT=your_postgres_port
- export PG_HOST=your_postgres_host
## Requirements
To use tsuki-wscp, you will need the following:
- Python 3
- Live PostgreSQL database
- "wscp_data" table with columns "message, source"
- Firefox Developer browser

You can install Python 3 and PostgreSQL from their respective websites. To install Firefox Developer browser, [visit the official website.](https://www.mozilla.org/en-US/firefox/developer/)