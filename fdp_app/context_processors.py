#!/usr/bin/env python
# -*- coding: utf-8 -*-

import models
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from views import get_all_pictures_in_event

def is_element_already_logged(new_element, modification_list):
    for previous_entry in modification_list :
        if previous_entry['title'] == new_element['title'] and previous_entry['name'] == new_element['name']:
            return True
        if previous_entry['name'] == new_element['name'] :
            return True
    return False

def common(request):
    user = None
    if request.user.is_authenticated():
        user = request.user
    all_sections = models.Section.objects.all().order_by('name')

    recentActions = LogEntry.objects.all().order_by('action_time').reverse()

    next_events = models.Event.objects.filter(date__gte=datetime.now()).order_by('date')[:10]

    modification_list = list()
    for each in recentActions:
        new_element = dict()
        if each.content_type.name == 'section' or each.content_type.name == 'picture' or each.content_type.name == 'event':
            new_element['type'] = each.content_type.name
            try :
                edited_object = each.get_edited_object()
            except Exception:
                edited_object = None
            if edited_object and (each.is_change or each.is_addition) : 
                if each.content_type.name == 'picture' :
                    new_element['name'] = edited_object.event.name
                    new_element['pictures'] = get_all_pictures_in_event(edited_object.event)
                    if each.is_change() :
                        new_element['title'] = 'Photo modifiée :'
                    else :
                        new_element['title'] = 'Nouvelle(s) photo(s) :'
                elif each.content_type.name == 'section' : 
                    new_element['name'] = edited_object.name
                    new_element['pictures'] = [edited_object.picture]
                    if each.is_change() : 
                        new_element['title'] = 'Description modifiée :'
                    else :
                       new_element['title'] = 'Nouvelle section :' 
                elif each.content_type.name == 'event' :
                    new_element['name'] = edited_object.name
                    new_element['pictures'] = get_all_pictures_in_event(edited_object)
                    if each.is_change() : 
                        new_element['title'] = 'Description modifiée :'
                    else : 
                        new_element['title'] = 'Nouvel évènement :'

                if not is_element_already_logged(new_element, modification_list) :
                    modification_list.append(new_element)
            if len(modification_list)>5 :
                break

    return {
        'username': user,
        'all_sections': all_sections,
        'recent_change': modification_list,
        'next_events': next_events,
    }


