import json

import wtforms as wt
from flask import Blueprint, Response, render_template, request
from flask_wtf import Form
from wtforms import TextField

from app import db
from app.models import Tag, Video

youtube = Blueprint('youtube', __name__)


class FilterForm(Form):
    autocomp = TextField('Filter by tags', id='autocomplete')


@youtube.route('/autocomplete', methods=['GET'])
def autocomplete():
    search = request.args.get('term', '')
    tags = [
        tag.tagname
        for tag in Tag.query.filter(Tag.tagname.like(search + '%')).all()
    ]
    return Response(json.dumps(tags), mimetype='application/json')


@youtube.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """display collected data"""
    form = FilterForm(request.form)
    if request.method == 'POST':
        if form.autocomp.data == '':
            videos = Video.query.all()
        else:
            tag = Tag.query.filter_by(tagname=form.autocomp.data).first()
            if tag:
                videos = Video.query.filter(Video.tags.any(id=tag.id)).all()
            else:
                videos = []

    if request.method == 'GET':
        videos = Video.query.all()
    return render_template('youtube/dashboard.html', videos=videos, form=form)
