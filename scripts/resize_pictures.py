# -*- coding: utf-8 -*-

import os
import subprocess
import imghdr

IMAGES_EXTENSIONS = ('.png', '.gif', '.jpg', '.bmp', '.jpeg')

PICTURE_DIRS = '/media/datas/pictures/user_pictures/'

def get_image_size(image_path):
    try :
        result = subprocess.getoutput('identify %s' %image_path)
        #result example :
        #P1060285.JPG JPEG 4000x3000 4000x3000+0+0 8-bit DirectClass 5.326MB 0.000u 0:00.009
        image_infos  = result.split(' ')
        image_resolution = image_infos[2].split('x')
        return int(image_resolution[0]),int(image_resolution[1])
    except Exception as e:
        #print 'could not find image size :', Exception, e
        return 0,0

def resize_image(image_path):
    os.system('mogrify -resize 1280 %s' %image_path)

def check_and_resize_image(image_path):
    if os.path.splitext(image_path.lower())[-1] in IMAGES_EXTENSIONS:
        width, height = get_image_size(image_path)
        #print 'current image size : ', width, height 
        if width >1280 :
            print('resize image %s size %sx%s' %(image_path, width, height))
            resize_image(image_path)
            return 1
        return 0

def check_and_resize_dir(dirname):
    listdirectory = os.listdir(dirname)
    progress = 0
    nb_file_resized = 0
    for i,filename in enumerate(listdirectory) :
        current_progress = int(i/float(len(listdirectory))*100)
        if current_progress != progress :
            progress = current_progress
            print('progress : ', progress)
        resized = check_and_resize_image(os.path.join(dirname, filename))
        if resized : nb_file_resized += 1
    print('resize done nb files : %s resized : %s' %(len(listdirectory),nb_file_resized))

if __name__ == "__main__":
    import sys
    directory = PICTURE_DIRS
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    check_and_resize_dir(directory)
