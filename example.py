__author__ = 'paunin'

from hhParser import hhParser

worker = hhParser.worker(1, 10, '/var/www/images')

for empl in worker:
    print(empl.logo)

