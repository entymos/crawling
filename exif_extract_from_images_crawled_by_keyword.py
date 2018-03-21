#-*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os
from fake_useragent import UserAgent as FakeUserAgent
from PIL import Image
from PIL.ExifTags import TAGS

def get_exif(_image_file_name):
    try:
        ret = {}
        i = Image.open(_image_file_name)
        info = i._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        return ret
    except IOError as io_e:
        #print(io_e)
        print('Cannot open this file ("',_image_file_name,'")')
    except AttributeError as at_e:
        #print(at_e)
        print('This image has no exif information ("',_image_file_name,'")')

def print_exif(image_name):
    exif = get_exif(image_name)
    exif_string = ''

    if 'DateTime' in exif:
        exif_string = 'Date Time ' + str(exif['DateTime']) + "\n"
    if 'LensModel' in exif:
        exif_string += 'Lens Model ' + str(exif['LensModel']) + "\n"
    if 'FocalLength' in exif:
        exif_string += 'Focal Length ' + str(exif['FocalLength'][0]) + 'mm' + "\n"
    if 'ExposureTime' in exif:
        exposureTime = exif['ExposureTime']
        if exposureTime[0] ==1:
            exif_string += 'Exposure Time ' + '1/' + str(exposureTime[1]) + "\n"
        elif exposureTime[1] == 1:
            exif_string += 'Exposure Time ' + str(exif['ExposureTime'][0]) + 's' + "\n"
    if 'FNumber' in exif:
        exif_string += 'F Number ' + 'f' + str(exif['FNumber'][0]) + "\n"
    if 'ISOSpeedRatings' in exif:
        exif_string += 'ISO ' + str(exif['ISOSpeedRatings']) + "\n"

    print(exif_string)

def google_scrape_images_by_keyword(query, language):
    results = []
    fake_ua = FakeUserAgent()

    #images
    print('[%s] https://www.google.co.kr/search?hl=ko&q=%s&tbm=isch' % (str(query), str(query)))
    query_url='https://www.google.co.kr/search?hl=ko&q=%s&tbm=isch&tbs=isz:lt,islt:2mp' % (str(query))
        
    headers = {
                'User-Agent': fake_ua.random, #'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
                'Content-Type': 'text/plain;charset=UTF-8',
                'Accept': 'text/html,application/xhtml+xml,application/xml; q=0.9,image/webp,*/*;q=0.8'
                }
    params = {
        'hl': language,
        'origin': 'https://www.google.co.kr', #
        'uc': 1,
        'xhr': 1
    }

    source_code = requests.get(url=query_url, params=params, headers=headers, allow_redirects=True)
    
    if not source_code.status_code == 200: #check if webpage exists
        return []

    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")        

    for div in soup.findAll('div', attrs={'class':'rg_meta'}):
        try:
            resdata = str(div.findAll(text=True)).replace(u'\xa0', u' ').replace('[\'','').replace('\']','')
            resdata_json = json.loads(resdata) 
            resdata_json_image = resdata_json['ou']            
            results.append(resdata_json_image)
        except Exception as ee:
            print(ee)

    time.sleep(random.randrange(9,20))

    return results

def imagesByKeyword(resfolder, keyword, language, topN):
    #final result folder
    dirname = 'C:/Users/yoon/Desktop/%s' % (resfolder)
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    #search images by keywords
    images = google_scrape_images_by_keyword(keyword, language)

    #find or create folder for each keywords
    dirname = 'C:/Users/yoon/Desktop/%s/%s' % (resfolder, keyword)
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    imgCnt = 0
    for imageUrl in images[:topN]:
        print('now downloading...: ' + imageUrl)

        try:
            #save images
            fileName = '%s/%s_%03d.png' % (dirname,keyword,imgCnt)
            f = open(fileName,'wb')
            f.write(requests.get(imageUrl).content)
            f.close()

            imgCnt += 1
            print('downloaded')

            print_exif(fileName)
        except:
            print('failed to download')

if __name__ == '__main__':

    imagesByKeyword('images', 'grand canyon photos','kr',200)

    print("********************DONE***************************")
    #input()
    #exit(0)
