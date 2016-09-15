#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from django import forms

from fdp_app import models

logger = logging.getLogger('fdp_app.forms')


class EventForm(forms.ModelForm):
    file = forms.FileField(required=False)

    class Meta:
        model = models.Event
        fields = ('name', 'content', 'date')


class PictureForm(forms.Form):
    file = forms.FileField(required=True)


class ModifyEventForm(forms.ModelForm):
    def __init__(self, all_sections, *args, **kwargs):
        super(ModifyEventForm, self).__init__(*args, **kwargs)
        self.fields['section'] = forms.ChoiceField(choices=[(s['section__id'], s['section__name']) for s in all_sections])

    class Meta:
        model = models.Event
        fields = ('name', 'content', 'date')


class ModifySectionForm(forms.ModelForm):
    class Meta:
        model = models.Section
        fields = ('content', 'schedule', 'picture')
