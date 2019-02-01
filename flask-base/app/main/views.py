import requests
from flask import Blueprint, g, render_template
from flask.ext.rq import job

from app.models import Channel, EditableHTML, Tag, Video
from app.utils import get_channel_info, get_channel_videos

from .. import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', editable_html_obj=editable_html_obj)


@main.route('/datacollect')
def datacollect():
    pass


@main.route('/getvideos/<channel_id>')
def getvideos(channel_id):
    channel_info = get_channel_info(channel_id)
    channel = Channel(channelId=channel_id, **channel_info)

    videos = get_channel_videos(channel_id)
    db.session.add()
    return render_template('main/channel.html', ids=videos)
