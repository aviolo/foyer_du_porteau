# -*- coding: utf-8 -*-
import models
import os
from datetime import datetime
from fdp_app.models import Section
from fdp_app.models import Event, Picture
from upload_utils import save_files

from django.conf import settings
from django.contrib.admin import widgets
#from django.contrib.admin.widgets import AdminDateWidget 
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
import django.dispatch
from django.forms import ModelForm, Textarea, ModelChoiceField, ChoiceField, DateTimeField, FileField, Form
from django.forms.fields import DateField
from django.forms.extras.widgets import SelectDateWidget
from django.template import defaultfilters, RequestContext
from django.shortcuts import render_to_response
from django.shortcuts import render

import logging
logger = logging.getLogger(__name__)

#handle errors
def on_error(text, will_send_mail=True):
    logger.error(text)
    mails = [admin[1] for admin in settings.ADMINS]
    if will_send_mail :
        send_mail('Error from foyerduporteau.net', text , 'lancereau.flavie@gmail.com', mails , fail_silently=False)


def error500(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response

#Forms
class EventForm(ModelForm):
    file = FileField(required=False)
    class Meta:
        model = Event
        fields = ('name', 'content', 'section', 'date')
        #fields = ('name', 'content', 'section', 'date', 'last_modification_date')

class PictureForm(Form):
    event = ChoiceField()
    file = FileField(required=True)

#views
def home_construction_view(request):
    return render_to_response("fdp_app/home_construction_view.html", context_instance=RequestContext(request))

def home_view(request):
    home_sections = None
    all_events = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError,e:
        on_error('Error in home view : %s' %e)
    content = { 'home_sections' : home_sections, 'all_events' : all_events,}
    return render_to_response("fdp_app/home_view.html", content, context_instance=RequestContext(request))

def modify_profile_view(request):
    home_sections = None
    all_events = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError,e:
        on_error('Error in modify profile view : %s' %e)
    content = { 'home_sections' : home_sections, 'all_events' : all_events,}
    return render_to_response("fdp_app/modify_profile_view.html", content, context_instance=RequestContext(request))

def modify_event_view(request):
    #event_form = EventForm()
    home_sections = None
    all_events = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError,e:
        on_error('Error in modify event view : %s' %e)
    content = { 'home_sections' : home_sections, 'all_events' : all_events,}#'event_form' : event_form,
    return render_to_response("fdp_app/modify_event_view.html", content, context_instance=RequestContext(request))

def add_event_view(request):
    home_sections = None
    all_events = None
    event_form = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError,e:
        on_error('Error in add event view 1 : %s' %e)
    user = request.user
    the_user = models.User.objects.filter(username=user)[0]
    section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
    section_list =  section_query.values('section__name', 'section__id')
    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=Event(user_id=the_user.id))
        event_form.fields['section'].choices = [(s['section__id'], s['section__name']) for s in section_list]
        if event_form.is_valid():
            try:
                new_event = event_form.save()
                if request.FILES:
                    event = get_event_by_name(request.POST["name"])
                    year = str(event.date.year)
                    section_name = get_section(event.section_id)
                    section_name = defaultfilters.slugify(section_name)
                    event_name = defaultfilters.slugify(event.name)
                    save_files(request.FILES['file'], year, section_name, event_name, new_event.pk, the_user.id)
            except IndexError,e:
                on_error('Error in add event view 2 : %s' %e)
            content = { 'home_sections' : home_sections,'all_events' : all_events, }
            return render_to_response("fdp_app/menu_view.html", content, context_instance=RequestContext(request))
        else:
            on_error('le formulaire est mal rempli', will_send_mail=False)
    else:
        event_form = EventForm(request.POST, request.FILES, instance=Event(user_id=the_user.id))
        event_form.fields['section'].choices = [(s['section__id'], s['section__name']) for s in section_list]
    csrfContext = RequestContext(request)
    content = { 'home_sections' : home_sections, 'all_events' : all_events, 'event_form' : event_form,}
    return render_to_response("fdp_app/add_event_view.html", content, context_instance=csrfContext)

def add_picture_view(request):
    home_sections = None
    all_events = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError,e:
        on_error('Error in add picture view 1 : %s' %e)
    user = request.user
    the_user = models.User.objects.filter(username=user)[0]
    event_list = get_all_events()
    event_list = models.Event.objects.all()
    if request.method == 'POST':
        picture_form = PictureForm(request.POST, request.FILES)
        picture_form.fields['event'].choices = [(e.id, e.name) for e in event_list]
        if picture_form.is_valid():
            event = None
            try:
                event_id = -1
                for val in picture_form.fields['event'].choices:
                    if int(val[0]) == int(picture_form.cleaned_data['event']):
                        event_id =  val[0]
                        break
                if event_id > 0:
                    event = get_event_by_id(event_id)
                    year = str(event.date.year)
                    section_name = get_section(event.section_id)
                    section_name = defaultfilters.slugify(section_name)
                    event_name = defaultfilters.slugify(event.name)
                    save_files(request.FILES['file'], year, section_name, event_name, event_id, the_user.id)
            except IndexError,e:
                on_error('Error in add picture view 2 : %s' %e)
        content = {'home_sections' : home_sections, 'all_events' : all_events,}
        return render_to_response("fdp_app/menu_view.html", content , context_instance=RequestContext(request))
    else:
        picture_form = PictureForm(request.POST, request.FILES)
        picture_form.fields['event'].choices = [(e.id, e.name) for e in event_list]
    csrfContext = RequestContext(request)
    content = {'home_sections' : home_sections, 'all_events' : all_events, 'picture_form' : picture_form,}
    return render_to_response("fdp_app/add_picture_view.html", content, context_instance=csrfContext)

def menu_view(request):
    home_sections = None
    all_events = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError,e:
        on_error('Error in menu view : %s' %e)
    content = {'home_sections' : home_sections, 'all_events' : all_events,}
    return render_to_response("fdp_app/menu_view.html", content, context_instance=RequestContext(request))    

def logout_view(request):
    logout(request)
    home_sections = None
    all_events = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError,e:
        on_error('Error in logout view : %s' %e)
    content = {'home_sections' : home_sections, 'all_events' : all_events, 'username' : None, }
    return render_to_response("fdp_app/home_view.html", content, context_instance=RequestContext(request))

def login_view(request):
    state = "Please log in below..."
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                home_sections = None
                all_events = None
                try:
                    home_sections = get_section_infos('foyerduporteau')
                    all_events = get_next_thrid_event_in_section(home_sections['index'])
                except IndexError,e :
                    on_error('Error in login view : %s' %e)
                content = {'home_sections' : home_sections, 'all_events' : all_events, 'username' : user,}
                return render_to_response("fdp_app/home_view.html", content, context_instance=RequestContext(request))
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    content = {'state':state,}
    return render_to_response('fdp_app/login_view.html', content, context_instance=RequestContext(request))

def section_view(request, section_slug):
    all_events = None
    contents_sections = None
    section_contact = None
    try:
        contents_sections = get_section_infos(section_slug)
        section_contact = get_section_contact(contents_sections['index'])
        all_events = get_all_event_in_section(contents_sections['index'])
    except IndexError, e:
        on_error('Error in section %s view : %s' %(section_slug,e))
    content = { 'contents_sections' : contents_sections, 'section_contact' : section_contact, 'all_events' : all_events,}
    return render_to_response("fdp_app/section_view.html", content, context_instance=RequestContext(request))

def infos_view(request, section_slug):
    all_events = None
    contents_sections = None
    try:
        contents_sections = get_section_infos(section_slug)
        all_events = get_all_event_in_section(contents_sections['index'])
    except IndexError,e:
        on_error('Error in infos %s view : %s' %(section_slug,e))
    content = { 'contents_sections' : contents_sections,'all_events' : all_events, }
    return render_to_response("fdp_app/infos_view.html", content, context_instance=RequestContext(request))

def pictures_view(request):
    all_events = list()
    for event in models.Event.objects.filter(date__lte=datetime.now()).order_by('date').reverse():
        if event:
            event.pictures = get_all_pictures_in_event(event)
            if len(event.pictures) > 1:
                all_events.append(event)
    return render_to_response("fdp_app/pictures_view.html", {'all_events':all_events }, context_instance=RequestContext(request))

def event_view(request, section_slug, event_slug):
    event = models.Event.objects.filter(id=event_slug)[0]
    event.pictures = get_all_pictures_in_event(event)
    return render_to_response("fdp_app/event_view.html", {'event':event }, context_instance=RequestContext(request))

# get functions
def get_section_infos(section):
    section = models.Section.objects.filter(url=section)[0]
    contents_sections = dict(index=section.id, name=section.name, content=section.content, picture=section.picture, schedule=section.schedule, url=section.url)
    return contents_sections

def get_section(section_id):
    section_name = None
    section = Section.objects.filter(id=section_id)[0]
    return section.name

def get_section_contact(index):
    section_contact = list()
    try:
        contacts = models.UserSection.objects.filter(right__id=4, section__id=index)
        for contact in contacts :
            if contact :
                section_contact.append(dict(name=contact.user.get_full_name(),number_phone=contact.user.userprofile.number_phone ))
    except IndexError:
        section_contact = list()
    return section_contact

def get_next_thrid_event_in_section(index):
    all_events = list()
    #event = models.Event.objects.filter(section_id=index, date__gt=datetime.now()).order_by('date')[:3]
    for event in models.Event.objects.filter(section_id=index, date__gt=datetime.now()).order_by('date')[:3]:
        if event:
            event.pictures = get_all_pictures_in_event(event)
            all_events.append(event)
    return all_events

def get_all_event_in_section(index):
    all_events = list()
    for event in models.Event.objects.filter(section_id=index).order_by('date').reverse():
        if event:
            event.pictures = get_all_pictures_in_event(event)
            all_events.append(event)
    return all_events

def get_event_by_name(name):
    return models.Event.objects.all().filter(name=name)[0]

def get_event_by_id(index):
    return models.Event.objects.all().filter(id=index)[0]

def get_all_events():
    all_events = list()
    for event in models.Event.objects.all().order_by('date').reverse():
        all_events.append(event)
    return all_events

def get_all_pictures_in_event(event):
    event.pictures = list()
    for picture in models.Picture.objects.filter(event_id=event.id):
        if picture:
            event.pictures.append(picture)
            picture.miniature = 'miniatures/%s' %picture.filename
    return event.pictures
