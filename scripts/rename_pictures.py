# -*- coding: utf-8 -*-

#user_pictures/P1040175 (Copier).JPG
#user_pictures/p1040175-copier.jpg
#select filename from fdp_app_picture where locate('(', filename)
#update fdp_app_picture set filename=lower(replace(replace(filename, " ", "-"), "(", ""))) where like "% (%";
#select filename from fdp_app_picture where locate('(', filename)
#update fdp_app_picture set filename=lower(replace(replace(filename, " ", "-"), "(", "")) where filename like "%(%"
#update fdp_app_picture set filename=lower(replace(replace(replace(filename, " ", "-"), "(", ""), ")", "")) where filename like "%)%"

import os
from django.template import defaultfilters
from os import listdir
from os.path import isfile, join

PICTURE_DIRS = '/kunden/homepages/45/d118779996/htdocs/src/fdp_django/stable/medias/user_pictures/'
MINIATURE_DIRS = '/kunden/homepages/45/d118779996/htdocs/src/fdp_django/stable/medias/miniatures/user_pictures'


def add_img_to_db(image_file_path, event_id=None, user_id=None):
    miniature_file = os.path.split(os.path.basename(image_file_path))[1]
    miniature_path = os.path.join(MINIATURE_DIRS, miniature_file)
    os.system('cp %s %s' %(image_file_path, miniature_path))
    os.system('mogrify -resize 250 %s' %miniature_path)

file_list = list()
index = 0
for f in listdir(PICTURE_DIRS):
    if isfile(join(PICTURE_DIRS, f)):
        filename = join(PICTURE_DIRS, f)
        if "(" in filename:
            index += 1
            file_list.append(filename)

for f in file_list:
    filename = os.path.split(os.path.basename(f))[1]
    filename, extension_file = os.path.splitext(filename)
    new_filename = defaultfilters.slugify(filename)
    new_extension = defaultfilters.slugify(extension_file)
    filename = os.path.join(new_filename + '.' + new_extension)
    file_path = os.path.join(os.path.dirname(f), filename)
    cmd = 'mv \'%s\' %s' %(f, file_path)
    os.system(cmd.encode('utf-8'))
    add_img_to_db(file_path)

