#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

from fdp_app import models
from fdp_app.views import get_all_pictures_in_event


def is_element_already_logged(new_element, modification_list):
    for previous_entry in modification_list:
        if previous_entry['title'] == new_element['title'] and previous_entry['name'] == new_element['name']:
            return True
        if previous_entry['name'] == new_element['name']:
            return True
    return False


def common(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    all_sections = models.Section.objects.all().order_by('name')

    next_events = models.Event.objects.filter(date__gte=datetime.now()).order_by('date')[:10]

    modification_list = models.Event.objects.all().order_by('last_modification_date').reverse()[:5]

    for event in modification_list:
        if event:
            event.pictures = get_all_pictures_in_event(event)
            event.section_slug = event.section.url

    return {
        'username': user,
        'all_sections': all_sections,
        'recent_change': modification_list,
        'next_events': next_events,
    }
