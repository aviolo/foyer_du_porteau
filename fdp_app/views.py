#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template import defaultfilters

from fdp_app import forms
from fdp_app import models
from fdp_app.upload_utils import save_files, move_picture_directory, check_type_file

logger = logging.getLogger('fdp_app.views')


# handle errors
def on_error(text, will_send_mail=True):
    logger.error(text)
    mails = [admin[1] for admin in settings.ADMINS]
    if will_send_mail:
        send_mail('Error from foyerduporteau.net', text, 'foyerduporteau@gmail.com', mails, fail_silently=False)


def home_construction_view(request):
    return render(request, "fdp_app/home_construction_view.html")


def home_view(request):
    home_sections = None
    all_events = None
    all_sections_authorization = None
    user = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
        user = request.user
        if user.is_active:
            the_user = models.User.objects.filter(username=user)[0]
            all_sections_right = models.UserSection.objects.filter(user_id=the_user.id, right__id=3).count()
            if all_sections_right >= 1:
                all_sections_authorization = list()
                for section in models.Section.objects.all():
                    all_sections_authorization.append({'section__id': section.id, 'section__name': section.name})
            else:
                section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
                all_sections_authorization = section_query.values('section__name', 'section__id')
            logger.info("authorization section : %s" % all_sections_authorization)
    except IndexError:
        pass
    return render(request, "fdp_app/home_view.html", {
        'home_sections': home_sections,
        'all_events': all_events,
        'autho_section': all_sections_authorization,
    })


@login_required
def modify_profile_view(request):
    home_sections = None
    all_events = None
    try:
        home_sections = get_section_infos('foyerduporteau')
        all_events = get_next_thrid_event_in_section(home_sections['index'])
    except IndexError as e:
        on_error('Error in modify profile view : %s' % e)
    return render(request, "fdp_app/modify_profile_view.html", {
        'home_sections': home_sections,
        'all_events': all_events
    })


@login_required
def modify_section_view(request, section_slug):
    try:
        sections_infos = get_section_infos(section_slug)
        section_changed = models.Section.objects.get(pk=sections_infos['index'])
    except IndexError as e:
        on_error('Erreur lors de la recuperation des donnees de sections : %s' % e)
    if request.method == 'POST':
        section_form = forms.ModifySectionForm(request.POST, request.FILES, instance=section_changed)
        if section_form.is_valid():
            try:
                section_changed.content = request.POST['content']
                section_changed.schedule = request.POST['schedule']
                section_changed.save()
                if request.FILES:
                    result = check_type_file(section_changed.picture)
                    if result:
                        section_changed.picture = result
                        section_changed.save()
                    else:
                        raise 'File uploaded is not an image'
            except Exception as e:
                on_error('Erreur lors de la modification des donnees de sections : %s' % e)
            section_contact = get_section_contact(sections_infos['index'])
            all_events = get_all_event_in_section(sections_infos['index'])
            if 'foyerduporteau' in sections_infos['slug']:
                return HttpResponseRedirect('/')
            content = {'contents_sections': sections_infos, 'section_contact': section_contact, 'all_events': all_events, }
            return HttpResponseRedirect('/%s' % (sections_infos['slug']), content)
        else:
            on_error('les donnees saisit dans le changement de section sont incorrectes', will_send_mail=False)
            content = modify_section_form(sections_infos)
            return render(request, "fdp_app/modify_section_view.html", content)
    else:
        content = modify_section_form(sections_infos)
    return render(request, "fdp_app/modify_section_view.html", content)


@login_required
def modify_event_view(request, section_slug, event_id):
    home_sections = None
    all_sections = None
    event_changed = None
    try:
        sections_infos = get_section_infos(section_slug)
        event = get_event_by_id(event_id)
        event_changed = models.Event.objects.get(pk=event.id)
    except IndexError as e:
        on_error('Error in add event view 1 : %s' % e)
    user = request.user
    the_user = models.User.objects.filter(username=user)[0]
    if request.method == 'POST':
        all_sections_right = models.UserSection.objects.filter(user_id=the_user.id, right__id=3).count()
        if all_sections_right >= 1:
            all_sections = list()
            for section in models.Section.objects.all():
                all_sections.append({'section__id': section.id, 'section__name': section.name})
        else:
            section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
            all_sections = section_query.values('section__name', 'section__id')
        old_data_event = models.Event.objects.get(pk=event.id)
        event_form = forms.ModifyEventForm(all_sections, request.POST, request.FILES, instance=event_changed)
        if event_form.is_valid():
            new_section = request.POST['section']
            try:
                old_name = old_data_event.name
                old_section = old_data_event.section_id
                all_pictures_to_move = get_all_pictures_in_event(old_data_event)
                updated_form = event_form.save()
                year = str(old_data_event.date.year)
                logger.info("old_section : %s, new_section : %s" % (old_section, new_section))
                if event_changed.name != old_name:
                    logger.info("changer le nom de l event")
                    section_name = get_section_name(old_data_event.section_id)
                    section_name = defaultfilters.slugify(section_name)
                    event_name = defaultfilters.slugify(event_changed.name)
                    move_picture_directory(year, section_name, section_name, event_name, old_name, all_pictures_to_move)
                    old_name = defaultfilters.slugify(event_changed.name)
                if request.FILES:
                    logger.info("Ajout de photos")
                    event = get_event_by_name(request.POST["name"])
                    year = str(event_changed.date.year)
                    section_name = get_section_name(event_changed.section_id)
                    section_name = defaultfilters.slugify(section_name)
                    event_name = defaultfilters.slugify(event_changed.name)
                    save_files(request.FILES['file'], year, section_name, event_name, updated_form.pk, the_user.id)
                if int(new_section) != int(old_section):
                    logger.info("section changed")
                    logger.info("%s" % event_changed.name.encode('utf8'))
                    event_name = defaultfilters.slugify(event_changed.name)
                    event_changed.section_id = new_section
                    new_section_name = defaultfilters.slugify(get_section_name(new_section))
                    old_section_name = defaultfilters.slugify(get_section_name(old_section))
                    event_changed.save()
                    move_picture_directory(year, old_section_name, new_section_name, event_name, old_name, all_pictures_to_move)
                    # UPDATE BDD chemin image
            except IndexError as e:
                on_error('Error in add event view 2 : %s' % e)
            section_contact = get_section_contact(sections_infos['index'])
            all_events = get_all_event_in_section(sections_infos['index'])
            if 'foyerduporteau' in sections_infos['slug']:
                return HttpResponseRedirect('/')
            content = {'contents_sections': sections_infos, 'section_contact': section_contact, 'all_events': all_events, }
            return HttpResponseRedirect('/%s' % (sections_infos['slug']), content)
        else:
            try:
                all_sections_right = models.UserSection.objects.filter(user_id=the_user.id, right__id=3).count()
                if all_sections_right >= 1:
                    all_sections = list()
                    for section in models.Section.objects.all():
                        all_sections.append({'section__id': section.id, 'section__name': section.name})
                else:
                    section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
                    all_sections = section_query.values('section__name', 'section__id')
                modify_event_form = forms.ModifyEventForm(all_sections)
                modify_event_form.fields['section'].initial = event.section_id
                modify_event_form.fields['name'].initial = event.name
                modify_event_form.fields['content'].initial = event.content
                modify_event_form.fields['date'].initial = event.date
            except IndexError as e:
                on_error('Error in modify event view 1 : %s' % e)
            on_error('les données sont incorrectes', will_send_mail=False)
    else:
        try:
            all_sections_right = models.UserSection.objects.filter(user_id=the_user.id, right__id=3).count()
            logger.info(all_sections_right)
            if all_sections_right >= 1:
                all_sections = list()
                for section in models.Section.objects.all():
                    all_sections.append({'section__id': section.id, 'section__name': section.name})
            else:
                section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
                all_sections = section_query.values('section__name', 'section__id')
            modify_event_form = forms.ModifyEventForm(all_sections)
            modify_event_form.fields['section'].initial = event.section_id
            modify_event_form.fields['name'].initial = event.name
            modify_event_form.fields['content'].initial = event.content
            modify_event_form.fields['date'].initial = event.date
        except IndexError as e:
            on_error('Error in modify event view 1 : %s' % e)
    return render(request, "fdp_app/modify_event_view.html", {
        'home_sections': home_sections,
        'all_events': all_sections,
        'modify_event_form': modify_event_form,
    })


@login_required
def add_event_view(request, section_slug):
    all_events = None
    event_form = None
    section_name = None
    sections_infos = None
    try:
        sections_infos = get_section_infos(section_slug)
    except IndexError as e:
        on_error('Error in add event view 1 : %s' % e)
    user = request.user
    the_user = models.User.objects.filter(username=user)[0]
    if request.method == 'POST':
        event_form = forms.EventForm(request.POST, request.FILES, instance=models.Event(user_id=the_user.id, section_id=sections_infos['index']))
        if event_form.is_valid():
            try:
                new_event = event_form.save()
                if request.FILES:
                    event = get_event_by_name(request.POST["name"])
                    year = str(event.date.year)
                    section_name = get_section_name(event.section_id)
                    section_name = defaultfilters.slugify(section_name)
                    event_name = defaultfilters.slugify(event.name)
                    save_files(request.FILES['file'], year, section_name, event_name, new_event.pk, the_user.id)
            except IndexError as e:
                on_error('Error in add event view 2 : %s' % e)
            section_contact = get_section_contact(sections_infos['index'])
            all_events = get_all_event_in_section(sections_infos['index'])
            if 'foyerduporteau' in sections_infos['slug']:
                return HttpResponseRedirect('/')
            content = {'contents_sections': sections_infos, 'section_contact': section_contact, 'all_events': all_events, }
            return HttpResponseRedirect('/%s' % (sections_infos['slug']), content)
        else:
            on_error('le formulaire est mal rempli', will_send_mail=False)
    else:
        event_form = forms.EventForm(request.POST, request.FILES, instance=models.Event(user_id=the_user.id))
    return render(request, "fdp_app/add_event_view.html", {
        'event_form': event_form,
    })


@login_required
def add_picture_view(request, section_slug, event_id):
    sections_infos = None
    all_events = None
    picture_form = None
    try:
        sections_infos = get_section_infos(section_slug)
    except IndexError as e:
        on_error('Error in add picture view 1 : %s' % e)
    user = request.user
    the_user = models.User.objects.filter(username=user)[0]
    if request.method == 'POST':
        picture_form = forms.PictureForm(request.POST, request.FILES)
        if picture_form.is_valid():
            try:
                event = get_event_by_id(event_id)
                event.last_modification_date = datetime.now()
                event.save()
                year = str(event.date.year)
                section_name = get_section_name(event.section_id)
                section_name = defaultfilters.slugify(section_name)
                event_name = defaultfilters.slugify(event.name)
                save_files(request.FILES['file'], year, section_name, event_name, event_id, the_user.id)
            except IndexError as e:
                on_error('Error in add picture view 2 : %s' % e)
        section_contact = get_section_contact(sections_infos['index'])
        all_events = get_all_event_in_section(sections_infos['index'])
        all_sections_right = models.UserSection.objects.filter(user_id=the_user.id, right__id=3).count()
        if all_sections_right >= 1:
            all_sections_authorization = list()
            for section in models.Section.objects.all():
                all_sections_authorization.append({'section__id': section.id, 'section__name': section.name})
        else:
            section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
            all_sections_authorization = section_query.values('section__name', 'section__id')
        if 'foyerduporteau' in sections_infos['slug']:
            return HttpResponseRedirect('/')
        content = {'contents_sections': sections_infos, 'section_contact': section_contact, 'all_events': all_events, 'autho_section': all_sections_authorization}
        return HttpResponseRedirect('/%s' % (sections_infos['slug']), content)
    else:
        picture_form = forms.PictureForm(request.POST, request.FILES)
    return render(request, "fdp_app/add_picture_view.html", {
        'home_sections': sections_infos,
        'all_events': all_events,
        'picture_form': picture_form,
    })


def section_view(request, section_slug):
    all_events = None
    contents_sections = None
    section_contact = None
    all_sections_authorization = None
    try:
        contents_sections = get_section_infos(section_slug)
        section_contact = get_section_contact(contents_sections['index'])
        all_events = get_all_event_in_section(contents_sections['index'])
        user = request.user
        if user.is_active:
            the_user = models.User.objects.filter(username=user)[0]
            all_sections_right = models.UserSection.objects.filter(user_id=the_user.id, right__id=3).count()
            if all_sections_right >= 1:
                all_sections_authorization = list()
                for section in models.Section.objects.all():
                    all_sections_authorization.append({'section__id': section.id, 'section__name': section.name})
            else:
                section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
                all_sections_authorization = section_query.values('section__name', 'section__id')
    except IndexError:
        pass
    return render(request, "fdp_app/section_view.html", {
        'contents_sections': contents_sections,
        'section_contact': section_contact,
        'all_events': all_events,
        'autho_section': all_sections_authorization,
    })


def infos_view(request, section_slug):
    all_events = None
    contents_sections = None
    try:
        logger.info("%s" % section_slug)
        contents_sections = get_section_infos(section_slug)
        logger.info("%s" % contents_sections['index'])
        all_events = get_all_event_in_section(contents_sections['index'])
        logger.info(all_events)
    except IndexError as e:
        on_error('Error in infos %s view : %s' % (section_slug, e))
    return render(request, "fdp_app/infos_view.html", {
        'contents_sections': contents_sections,
        'all_events': all_events,
    })


def activites_view(request):
    # all_sections = models.Section.objects.all().order_by('name')
    return render(request, "fdp_app/activites_view.html")


def pictures_view(request, year=''):
    user = None
    all_sections_authorization = None
    all_events = None
    if year == '':
        year = datetime.now().year
    all_events = list()
    if year != '0000':
        for event in models.Event.objects.filter(date__year=year, date__lte=datetime.now()).order_by('date').reverse():
            if event:
                event.pictures = get_all_pictures_in_event(event)
                all_events.append(event)
    else:
        for event in models.Event.objects.filter(date__gte=datetime.now()).order_by('date'):
            if event:
                event.pictures = get_all_pictures_in_event(event)
                all_events.append(event)
    years = list(set([event.date.year for event in models.Event.objects.filter(date__lte=datetime.now())]))
    try:
        user = request.user
        if user.is_active:
            the_user = models.User.objects.filter(username=user)[0]
            all_sections_right = models.UserSection.objects.filter(user_id=the_user.id, right__id=3).count()
            if all_sections_right >= 1:
                all_sections_authorization = list()
                for section in models.Section.objects.all():
                    all_sections_authorization.append({'section__id': section.id, 'section__name': section.name, 'section__slug': section.slug})
            else:
                section_query = models.UserSection.objects.filter(user_id=the_user.id, right__id=4)
                all_sections_authorization = section_query.values('section__name', 'section__id', 'section__slug')
    except IndexError as e:
        on_error('Error in pictures view 1 : %s' % e)
    return render(request, "fdp_app/pictures_view.html", {
        'years': years,
        'all_events': all_events,
        'autho_section': all_sections_authorization,
    })


def event_view(request, section_slug, event_id):
    event = get_object_or_404(models.Event, id=event_id)
    event.pictures = get_all_pictures_in_event(event)
    return render(request, "fdp_app/event_view.html", {'event': event})


# get functions

def modify_section_form(section_infos):
    try:
        modify_section_form = forms.ModifySectionForm()
        modify_section_form.fields['picture'].initial = section_infos['picture']
        modify_section_form.fields['content'].initial = section_infos['content']
        modify_section_form.fields['schedule'].initial = section_infos['schedule']
    except IndexError as e:
        on_error('Erreur lors du chargement du formulaire de section : %s' % e)
    content = {'modify_section_form': modify_section_form}
    return content


def get_section_infos(slug):
    try:
        section = models.Section.objects.filter(slug=slug)[0]
    except IndexError:
        raise Http404()
    logger.info("in get section infos : %s" % section)
    contents_sections = dict(index=section.id, name=section.name, content=section.content, picture=section.picture, schedule=section.schedule, slug=section.slug)
    return contents_sections


def get_section_name(section_id):
    section = models.Section.objects.filter(id=section_id)[0]
    return section.name


def get_section_contact(index):
    section_contact = list()
    try:
        contacts = models.UserSection.objects.filter(right__id=4, section__id=index)
        for contact in contacts:
            if contact:
                section_contact.append(dict(name=contact.user.get_full_name(), number_phone=contact.user.userprofile.number_phone))
    except IndexError:
        section_contact = list()
    return section_contact


def get_next_thrid_event_in_section(index):
    all_events = list()
    # event = models.Event.objects.filter(section_id=index, date__gt=datetime.now()).order_by('date')[:3]
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


def get_section_by_name(name):
    section = models.Section.objects.all().filter(name=name)[0]
    contents_sections = dict(index=section.id, name=section.name, content=section.content, picture=section.picture, schedule=section.schedule, slug=section.slug)
    return contents_sections


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
            picture.miniature = 'miniatures/%s' % picture.filename
    return event.pictures
