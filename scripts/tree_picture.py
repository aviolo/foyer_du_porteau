#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# changer filename dans tale picture 100->255
# changer picture dans section 100->255
# changer picture_filename dans userprofile 100->255

sys.path.append("/kunden/homepages/45/d118779996/htdocs/src/fdp_django/stable")
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.db import models
from fdp_app.models import Section
from fdp_app.models import Event, Picture
from django.template import defaultfilters

PICTURE_DIRS = '/kunden/homepages/45/d118779996/htdocs/src/fdp_django/stable/medias/user_pictures/'
MINIATURE_DIRS = '/kunden/homepages/45/d118779996/htdocs/src/fdp_django/stable/medias/miniatures/user_pictures/'

def get_all_pictures_in_event(event):
    event.pictures = list()
    for pictures in Picture.objects.filter(event_id=event.id):
        if pictures:
            event.pictures.append(pictures)
            pictures.miniature = 'miniatures/%s' %pictures.filename
    return event.pictures

def get_all_events():
    all_events = list()
    for event in Event.objects.all().order_by('date').reverse():
        event.pictures = get_all_pictures_in_event(event)
        all_events.append(event)
    return all_events

def get_section_by_event(section_id):
    section_name = None
    section = Section.objects.filter(id=section_id)[0]
    return section.name

def check_directory(year, section_name, event_name, pictures):
    year_dir = os.path.join(PICTURE_DIRS, year)
    year_min_dir = os.path.join(MINIATURE_DIRS, year)
    if not os.path.exists(year_dir) : os.mkdir(year_dir)
    if not os.path.exists(year_min_dir) : os.mkdir(year_min_dir)
    section_dir = os.path.join(year_dir, section_name)
    section_min_dir = os.path.join(year_min_dir, section_name)
    if not os.path.exists(section_dir) : os.mkdir(section_dir)
    if not os.path.exists(section_min_dir) : os.mkdir(section_min_dir)
    event_dir = os.path.join(section_dir, event_name)
    event_min_dir = os.path.join(section_min_dir, event_name)
    if not os.path.exists(event_dir) : os.mkdir(event_dir)
    if not os.path.exists(event_min_dir) : os.mkdir(event_min_dir)
    for picture in pictures:
        if picture:
            picture_name = str(picture.filename).split('/')[1]
            picture_path = os.path.join(PICTURE_DIRS, picture_name)
            if os.path.exists(picture_path):
                new_path_to_move = os.path.join(event_dir, picture_name)
                filename_bdd = os.path.join('user_pictures' + new_path_to_move.split("user_pictures")[1])
                if len(filename_bdd) > 250:
                    print("path is too big : %s" %filename_bdd)
                else:
                    p = Picture.objects.get(pk=picture.id)
                    p.filename = filename_bdd
                    p.save()
                    os.system('mv %s %s' %(picture_path, new_path_to_move))
                    miniature_path = os.path.join(MINIATURE_DIRS, picture_name)
                    new_path_to_move_min = os.path.join(event_min_dir, picture_name)
                    os.system('mv %s %s' %(miniature_path, new_path_to_move_min))

if __name__ == "__main__":
    all_event = get_all_events()
    for index, event in enumerate(all_event):
        year = str(event.date.year)
        section_name = get_section_by_event(event.section_id)
        new_section_name = defaultfilters.slugify(section_name)
        #print new_section_name
        new_event_name = defaultfilters.slugify(event.name)
        check_directory(year, new_section_name, new_event_name, event.pictures)
