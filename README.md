# Description

This is an application to monitor youtube channel data and collect information on how likes, dislikes, comments and favorites change overtime for each video in a channel. Keep in mind that google youtube api only allows 10000 requests per day. So monitoring large channels are not possible.

# Setup

The app is based on an excelent [flask-base](https://github.com/hack4impact/flask-base) boilerplate project.

The application requires to be run on python 3.6. Install the dependancies via `pipenv install`.  Install redis via your platform way. Set the required environment variables (you can store them in config.env file in `./flask-base` folder):

    DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/youtube
    SQLALCHEMY_DATABASE_URL=postgresql://postgres:mysecretpassword@localhost:5432/youtube
    DEV_DATABASE_URL=postgresql://{user}:{password}@{host}:{port}/{database}
    SECRET_KEY={seed for random functions}
    APP_NAME=Youtube-data-collector
    ADMIN_EMAIL=admin@admin.adm
    ADMIN_PASSWORD=password
    YOUTUBE_API_KEY={your youtube api key}

if you don't set the `DATABASE_URL` the default sqlite database will be used in `flask-base/data-dev.sqlite`

after all this is done, initialize the database:

    $ cd flask-base
    $ python manage.py recreate_db
    $ python manage.py setup_dev
    
Start monitoring some youtube channel:
    
    $ python manage.py start_scraping --channel-id=UCwUizOU8pPWXdXNniXypQEQ
    
# Running the app

Run the app using `$ honcho start -f Local` this will run flask in gunicorn server, start 1 redis worker and start periodically monitoring youtube channels.

# TODO

Write tests and implement better exception handling.