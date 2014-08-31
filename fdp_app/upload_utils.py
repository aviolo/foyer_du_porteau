# -*- coding: utf-8 -*-
from django.template import defaultfilters

from fdp_app.models import Picture, User, Event

import imghdr
import zipfile
import os
import commands # Waring: deprecated !

IMAGES_EXTENSIONS = ('.png', '.gif', '.jpg', '.bmp', '.jpeg')

dezip_path = '/tmp/ufiles'
media_path = 'medias/user_pictures'
miniatures_dir = 'medias/miniatures/user_pictures'

def get_image_size(image_path):
    try :
        result = commands.getoutput('identify %s' %image_path)
        #result example :
        #P1060285.JPG JPEG 4000x3000 4000x3000+0+0 8-bit DirectClass 5.326MB 0.000u 0:00.009
        image_infos  = result.split(' ')
        image_resolution = image_infos[2].split('x')
        return int(image_resolution[0]),int(image_resolution[1])
    except Exception,e:
        #print 'could not find image size :', Exception, e
        return 0,0

def resize_image(image_path):
    os.system('mogrify -resize 1280 %s' %image_path)

def check_and_resize_image(image_path):
    if os.path.splitext(image_path.lower())[-1] in IMAGES_EXTENSIONS:
        width, height = get_image_size(image_path)
        #print 'current image size : ', width, height 
        if width >1280 :
            resize_image(image_path)
            return 1
        return 0

# gérer les 7zip, rar, tar.gz...
def save_files(uploaded_file, year, section_name, event_name, event_id, user_id):
    filename, extension_file = os.path.splitext(uploaded_file.name)
    new_filename = defaultfilters.slugify(filename)
    new_extension = defaultfilters.slugify(extension_file)
    filename = os.path.join(new_filename + '.' + new_extension)
    uploaded_file.name = filename
    image_type = imghdr.what(uploaded_file)
    file_path = os.path.join(dezip_path, uploaded_file.name)
    if not image_type :
        #the file is not an image
        #maybe a zip
        if zipfile.is_zipfile(uploaded_file):
            upload_result = handle_uploaded_file(uploaded_file, file_path)
            zfile = zipfile.ZipFile(file_path, 'r')
            if not os.path.exists(dezip_path) : os.mkdir(dezip_path)
            # Créer le repertoire zipname a coup de basename
            zipfile_path = zfile.filename.lower()[:-4]
            zipfile_name = os.path.basename(zipfile_path)
            directory_zip = os.path.join(dezip_path, zipfile_name)
            if not os.path.exists(directory_zip) : os.mkdir(directory_zip)
            valid_files = list()
            for index, name in enumerate(zfile.namelist()):
                #if name.lower()[-3:] in IMAGES_EXTENSIONS:
                if os.path.splitext(name.lower())[-1] in IMAGES_EXTENSIONS:
                    name_img = os.path.basename(name)
		    filename, extension_file = os.path.splitext(name_img)
		    new_filename = defaultfilters.slugify(filename)
		    new_extension = defaultfilters.slugify(extension_file)
		    name_img = os.path.join(new_filename + '.' + new_extension)
                    image_path = os.path.join(dezip_path, zipfile_name, name_img)
                    image_file = open(image_path, 'w+')
                    image_file.write(zfile.open(name).read())
                    image_file.close()
                    valid_files.append(image_path)
            for tmp_file_path in valid_files :
                image_type = imghdr.what(tmp_file_path)
                if image_type :
                    add_img_to_db(tmp_file_path, year, section_name, event_name, event_id, user_id)
            os.system('rm -rf %s' %dezip_path)
        else:
            pass
    else :
        upload_result = handle_uploaded_file(uploaded_file, file_path)
        add_img_to_db(file_path, year, section_name, event_name, event_id, user_id)

def add_img_to_db(image_file_path, year, section_name, event_name, event_id=None, user_id=None):
    #copy to the right directory
    filename = os.path.basename(image_file_path)
    file_name = os.path.abspath( __file__ )
    parent_dir = os.path.dirname(os.path.dirname(file_name))
    media_dir = os.path.join(media_path, year, section_name, event_name)
    min_dir = os.path.join(miniatures_dir, year, section_name, event_name)
    abs_dir_pictures = os.path.join(parent_dir, media_dir)
    abs_min_dir_pictures = os.path.join(parent_dir, min_dir)
    if not os.path.exists(abs_dir_pictures) : os.makedirs(abs_dir_pictures)
    if not os.path.exists(abs_min_dir_pictures) : os.makedirs(abs_min_dir_pictures)
    check_and_resize_image(image_file_path)
    cmd = 'mv \'%s\' %s' %(image_file_path, abs_dir_pictures)
    os.system(cmd.encode('utf-8'))
    #generate miniature
    new_path = os.path.join(abs_dir_pictures, filename)
    miniature_path = os.path.join(abs_min_dir_pictures, filename)
    os.system('cp %s %s' %(new_path, miniature_path))
    os.system('mogrify -resize 250 %s' %miniature_path)
    #save to database
    path_bdd = os.path.join(year, section_name, event_name, filename)
    new_picture = Picture(title =filename, filename ='user_pictures/%s' %path_bdd, user=User.objects.filter(id=user_id)[0], event=Event.objects.filter(id= event_id)[0] )
    new_picture.save()

##----------------------------------------------------------------------------------
## handle_uploaded_file function
## save uploaded file
##----------------------------------------------------------------------------------
def handle_uploaded_file(uploaded_file, upload_path):
    # check folder
    folder = os.path.dirname(upload_path)
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except Exception, e:
            return False, 'Error when trying to create folder for upload. Error is: %s' %e
    
    # create new file
    try:
        destination = open(upload_path, 'wb+')
    except Exception, e:
        return False, 'Error when trying to create file. Error is: %s' %e
    
    # write new file
    for chunk in uploaded_file.chunks():
        destination.write(chunk)
    destination.close()

    return True, 'File uploaded.'

def move_picture_directory(year, section_name, name_event, old_name_event, all_pictures_to_move):
    file_name = os.path.abspath( __file__ )
    parent_dir = os.path.dirname(os.path.dirname(file_name))
    old_media_dir = os.path.join(media_path, year, section_name, old_name_event)
    old_min_dir = os.path.join(miniatures_dir, year, section_name, old_name_event)
    abs_old_dir_pictures = os.path.join(parent_dir, old_media_dir)
    abs_old_min_dir_pictures = os.path.join(parent_dir, old_min_dir)
    new_media_dir = os.path.join(media_path, year, section_name, name_event)
    new_min_dir = os.path.join(miniatures_dir, year, section_name, name_event)
    abs_new_dir_pictures = os.path.join(parent_dir, new_media_dir)
    abs_new_min_dir_pictures = os.path.join(parent_dir, new_min_dir)
    cmd = 'mv \'%s\' \'%s\'' %(abs_old_dir_pictures, abs_new_dir_pictures)
    os.system(cmd.encode('utf-8'))
    cmd = 'mv \'%s\' %s' %(abs_old_min_dir_pictures, abs_new_min_dir_pictures)
    os.system(cmd.encode('utf-8'))
    for picture in all_pictures_to_move:
        filename = str(picture.filename)
        print filename
        print old_name_event, name_event
        filename = filename.replace(old_name_event, name_event)
        print filename
        picture.filename = filename
        picture.save()

if __name__ == "__main__":
    path = '/home/lavi/Documents/Randonnée du 05 Mars sur le Bois de Saint-Pierre.zip'
    event_id = 18
    user_id = 3
    save_files(path, event_id, user_id)
