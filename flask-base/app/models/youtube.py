import datetime

from .. import db


class Channel(db.Model):
    name = db.Column(db.String(100), unique=False)
    channelId = db.Column(db.String(100), unique=True, primary_key=True)
    description = db.Column(db.Text)
    videos = db.relationship(
        'Video', backref=db.backref('channel', lazy='joined'), lazy='select')

    def __repr__(self):
        return '<%r>' % self.name


tags = db.Table(
    'tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column(
        'video_id', db.Integer, db.ForeignKey('video.id'), primary_key=True))


class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False)
    videoId = db.Column(db.String(100), unique=True, nullable=False)
    tags = db.relationship(
        'Tag',
        secondary=tags,
        lazy='joined',
        backref=db.backref('pages', lazy='joined'))
    channelId = db.Column(db.String(100), db.ForeignKey('channel.channelId'))
    thumbnail = db.Column(db.String(300))
    publishedAt = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    stats = db.relationship(
        'Stats', backref=db.backref('video', lazy=True), lazy='select')

    def __repr__(self):
        return '<%r>' % self.title


class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    videoId = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    viewCount = db.Column(db.Integer)
    commentCount = db.Column(db.Integer)
    likeCount = db.Column(db.Integer)
    dislikeCount = db.Column(db.Integer)
    favoriteCount = db.Column(db.Integer)
    date = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String(100), unique=True)
