## tsuki-wscp [v0.2.0]
tsuki-wscp is a web scraper that provides data collection for AI model training
## Supported sources (more to come)
- 4Chan
- Reddit
- Twitter
## What to expect
![average rows a sec](https://i.gyazo.com/06451df4560e2bab153d61f1efd4dae5.png)
- Apx 100-130 data rows a second
- Constant 20-30% cpu usage
- 10-20 Mbps network usage
## [Linux] 
- Before running the script make sure you edit the ``.bashrc`` file with your DB credentials.
- Run ``pip install -r requirements.txt``
## [Windows]
- Open the Start menu and search for "Environment Variables".
- Click on "Edit the system environment variables".
- Click on the "Environment Variables" button.
- Under "User variables" (or "System variables" for all users), click the "New" button.
- Enter a variable name (e.g., DB_NAME) and its value (e.g., your_database_name).
- Repeat steps 4-5 for each environment variable.
- Click "OK" to save the changes.
- Run ``py -m pip install -r requirements.txt``

Note: You may need to restart your system to apply changes.
## Usage
[Linux] ```python3 tsuki-wscp [-s {1-5}] [--nsfw-toggle]```

[Windows] ```py tsuki-wscp [-s {1-5}] [--nsfw-toggle]```
- The ```-s``` option is used to specify the driver delay. The value should be between 1 and 5. A higher delay can help prevent your IP from being blocked by the website.
- The ```--nsfw-toggle``` option enables scraping of highly NSFW boards. Note that this option should only be used if you are of legal age and comfortable with such content. 
- Please keep in mind that even the default boards WILL HAVE nsfw content but not as much.
## Requirements
To use tsuki-wscp, you will need the following:
- Python 3
- Live PostgreSQL database
- "wscp_data" table with columns "message, source"
- Firefox Developer browser

You can install Python 3 and PostgreSQL from their respective websites. To install Firefox Developer browser, [visit the official website.](https://www.mozilla.org/en-US/firefox/developer/)
