__author__ = 'paunin'
import urllib.request
import urllib.parse
from xml.dom.minidom import *
from PIL import Image

import sys


class employer(object):
    id = None
    name = None
    logo = None
    site = None
    email = None
    description = None


class worker(object):
    __base_url = 'http://api.hh.ru/1/xml/employer/%(employer_id)d/'
    __index = None
    __headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
    __image_dir = None


    def __init__(self, index, max_index, img_dir='/tmp'):
        self.__index = index
        self.__max_index = max_index
        self.__image_dir = img_dir


    def __iter__(self):
        return self

    def __next__(self):
        while True:
            self.__index += 1
            if self.__index > self.__max_index:
                raise StopIteration

            url = self.__base_url % {'employer_id': self.__index}
            sys.stdout.write('Fetching url  %s\n' % url)

            try:
                req = urllib.request.Request(url, None, self.__headers)
                response = urllib.request.urlopen(req)
                the_page = response.read()
            except urllib.error.URLError as e:
                sys.stderr.write('No employer with id = %d\n' % self.__index)
                sys.stderr.write('%s\n' % e.reason)
                continue

            try:
                xml = parseString(the_page)
            except Exception:
                sys.stderr.write('Can\'t parse xml for employer with id = %d\n' % self.__index)
                continue

            errs = xml.getElementsByTagName('error')
            if len(errs):
                sys.stderr.write(
                    'Error for employer with id = %d: ' % self.__index + errs[0].attributes['status'].value + '\n')
                continue

            empl = employer()
            empl.id = self.__index

            empl.name = xml.getElementsByTagName('name')[0].firstChild.nodeValue

            full_descr_s = xml.getElementsByTagName('full-descriptions')
            if len(full_descr_s):
                empl.description = full_descr_s[0].firstChild.nodeValue

            logos = xml.getElementsByTagName('logos')
            if len(logos):
                for link in logos[0].getElementsByTagName('link'):
                    rel = link.attributes['rel'].value
                    href = link.attributes['href'].value
                    if rel == 'big':
                        empl.logo = href
                        break

            if empl.logo:
                base_url = self.__image_dir + '/empl_%d.img' % empl.id
                urllib.request.urlretrieve(empl.logo, base_url)
                img = Image.open(base_url)
                img.convert('RGB')
                try:
                    img.save(base_url + ".png")
                except IOError as e:
                    sys.stderr.write('Image save error for employer with id = %d\n ' % empl.id)
                    empl.logo = None

            links = xml.getElementsByTagName('link')
            if len(links):
                for link in links:
                    rel = link.attributes['rel'].value
                    if rel is 'related':
                        empl.site = link.attributes['href'].value

            return empl











