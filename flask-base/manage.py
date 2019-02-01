#!/usr/bin/env python
import datetime
import os
import subprocess

from flask_migrate import Migrate, MigrateCommand
from flask_rq import get_queue
from flask_script import Manager, Shell
from redis import Redis
from rq import Connection, Queue, Worker
from rq_scheduler import Scheduler

from app import create_app, db
from app.models import Channel, Role, Tag, User, Video
from app.utils import get_channel_info, get_channel_videos, scrape_channel
from config import Config

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def recreate_db():
    """
    Recreates a local database. You probably should not use this on
    production.
    """
    db.drop_all()
    db.create_all()
    db.session.commit()


@manager.option(
    '-n',
    '--number-users',
    default=10,
    type=int,
    help='Number of each model type to create',
    dest='number_users')
def add_fake_data(number_users):
    """
    Adds fake data to the database.
    """
    User.generate_fake(count=number_users)


@manager.command
def setup_dev():
    """Runs the set-up needed for local development."""
    setup_general()


@manager.command
def setup_prod():
    """Runs the set-up needed for production."""
    setup_general()


def setup_general():
    """Runs the set-up needed for both local development and production.
       Also sets up first admin user."""
    Role.insert_roles()
    admin_query = Role.query.filter_by(name='Administrator')
    if admin_query.first() is not None:
        if User.query.filter_by(email=Config.ADMIN_EMAIL).first() is None:
            user = User(
                first_name='Admin',
                last_name='Account',
                password=Config.ADMIN_PASSWORD,
                confirmed=True,
                email=Config.ADMIN_EMAIL)
            db.session.add(user)
            db.session.commit()
            print('Added administrator {}'.format(user.full_name()))


@manager.option(
    '-i',
    '--channel-id',
    default='UCVMAuwgr6s72Vlowid2EsbQ',
    type=str,
    help='Youtube channel id to start monitoring',
    dest='channel_id')
def start_scraping(channel_id):
    '''Initializes monitoring of the given youtube channel id'''
    channel_info = get_channel_info(channel_id)
    channel = Channel(channelId=channel_id, **channel_info)
    db.session.add(channel)
    db.session.commit()
    scrape_channel(channel_id)
    # TODO: make this work
    # run_worker()
    # queue = get_queue()
    # scheduler = Scheduler(queue=queue)
    # scheduler.schedule(
    #     scheduled_time=datetime.utcnow(),  # Time for first execution, in UTC timezone
    #     func=scrape_channel,  # Function to be queued
    #     args=[channel_id,],  # Arguments passed into function when executed,
    #     interval=app.config['TRACKING_INTERVAL'],  # Time before the function is called again, in seconds
    #     repeat=None,  # Repeat this number of times (None means repeat forever)
    # )


@manager.command
def scrape_once():
    scrape_channel('UCVMAuwgr6s72Vlowid2EsbQ')



@manager.command
def run_worker():
    """Initializes a slim rq task queue."""
    listen = ['default']
    conn = Redis(
        host=app.config['RQ_DEFAULT_HOST'],
        port=app.config['RQ_DEFAULT_PORT'],
        db=0,
        password=app.config['RQ_DEFAULT_PASSWORD'])

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()


@manager.command
def format():
    """Runs the yapf and isort formatters over the project."""
    isort = 'isort -rc *.py app/'
    yapf = 'yapf -r -i *.py app/'

    print('Running {}'.format(isort))
    subprocess.call(isort, shell=True)

    print('Running {}'.format(yapf))
    subprocess.call(yapf, shell=True)


if __name__ == '__main__':
    manager.run()
