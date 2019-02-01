import os

import requests
from flask import url_for
from wtforms.compat import text_type
from wtforms.fields import Field
from wtforms.widgets import HiddenInput

from app import db
from app.models import Channel, Stats, Tag, Video


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


class CustomSelectField(Field):
    widget = HiddenInput()

    def __init__(self,
                 label='',
                 validators=None,
                 multiple=False,
                 choices=[],
                 allow_custom=True,
                 **kwargs):
        super(CustomSelectField, self).__init__(label, validators, **kwargs)
        self.multiple = multiple
        self.choices = choices
        self.allow_custom = allow_custom

    def _value(self):
        return text_type(self.data) if self.data is not None else ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[1]
            self.raw_data = [valuelist[1]]
        else:
            self.data = ''


API_URL = 'https://www.googleapis.com/youtube/v3/'
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')


def get_channel_info(channel_id):
    params = {
        'api_key': YOUTUBE_API_KEY,
        'channel_id': channel_id,
    }
    request_string = API_URL + 'channels?part=snippet&id={channel_id}&key={api_key}'.format(
        **params)
    channel_info_page = requests.get(request_string).json()
    return {
        'name': channel_info_page['items'][0]['snippet']['title'],
        'description': channel_info_page['items'][0]['snippet']['description']
    }


def get_channel_videos(channel_id):
    '''Returns a full list of channel video ids'''
    params = {
        'api_key': YOUTUBE_API_KEY,
        'channel_id': channel_id,
    }
    request_string = API_URL + 'search?key={api_key}&channelId={channel_id}&part=id&order=date&maxResults=50'.format(
        **params)
    videos_page = requests.get(request_string)
    videoIds = [
        item['id']['videoId'] for item in videos_page.json()['items']
        if 'videoId' in item['id']
    ]
    nextPage = videos_page.json().get('nextPageToken', None)

    while nextPage:
        videos_page = requests.get(request_string +
                                   '&pageToken={}'.format(nextPage))
        videoIds += [
            item['id']['videoId'] for item in videos_page.json()['items']
            if 'videoId' in item['id']
        ]
        nextPage = videos_page.json().get('nextPageToken', None)

    return videoIds


def scrape_channel(channel_id):
    for videoId in get_channel_videos(channel_id):
        videoData = get_video_data(videoId)
        video = db.session.query(Video).filter_by(videoId=videoId).first()
        if video:
            pass
        else:
            video = Video(
                videoId=videoId,
                title=videoData['title'],
                channelId=channel_id,
                publishedAt=videoData['publishedAt'],
                description=videoData['description'],
                thumbnail=videoData['thumbnail'])
            db.session.add(video)
            db.session.commit()
            if videoData['tags']:
                for tag in videoData['tags']:
                    video.tags.append(get_or_create_tag(tag))
                    db.session.commit()

        stats = Stats(
            videoId=video.id,
            viewCount=videoData['viewCount'],
            commentCount=videoData['commentCount'],
            likeCount=videoData['likeCount'],
            dislikeCount=videoData['dislikeCount'],
            favoriteCount=videoData['favoriteCount'])
        db.session.add(stats)
        db.session.commit()


def get_video_data(video_id):
    params = {
        'api_key': YOUTUBE_API_KEY,
        'id': video_id,
    }
    request_string = API_URL + 'videos?part=statistics,%20snippet&id={id}&key={api_key}'.format(
        **params)
    response = requests.get(request_string).json()
    video_data = {}
    video_data['publishedAt'] = response['items'][0]['snippet']['publishedAt']
    video_data['title'] = response['items'][0]['snippet']['title']
    video_data['description'] = response['items'][0]['snippet']['description']
    video_data['thumbnail'] = response['items'][0]['snippet']['thumbnails'][
        'medium']['url']
    if 'tags' in response['items'][0]['snippet']:
        video_data['tags'] = response['items'][0]['snippet']['tags']
    else:
        video_data['tags'] = None
    video_data.update(
        response['items'][0]['statistics'])  # save all of the statistics
    return video_data


def get_or_create_tag(tagname):
    tag = db.session.query(Tag).filter_by(tagname=tagname).first()
    if tag:
        return tag
    else:
        tag = Tag(tagname=tagname)
        db.session.add(tag)
        return tag
