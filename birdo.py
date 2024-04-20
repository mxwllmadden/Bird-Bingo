# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 17:26:01 2024

@author: mbmad
"""

import requests as req
import ebird.api as ebirb
import urllib.parse
from simple_image_download import simple_image_download as simp
import random
from matplotlib import pyplot, image
import os
import pathlib
import datetime
import numpy as np

now = datetime.datetime.now().strftime('%y.%m.%d %H-%M')

# API KEYS
ebirdkey = 'APIKEY'



def getebirddata(lat, lon, getobs=False):
    data = ebirb.get_nearby_observations(ebirdkey, lat, lon, dist=2, back=30)
    loccodes = []
    for bird in data:
        if not bird['locId'] in loccodes:
            loccodes.append(bird['locId'])
    if len(loccodes) > 10:
        print('Consider reducing observation range')

    loccodes = loccodes[:10]
    if getobs is True:
        for bird in data:
            bird['numObs'] = len(ebirb.get_species_observations(
                ebirdkey, bird['speciesCode'], loccodes))

    return data


def getloc(address):
    url = 'https://nominatim.openstreetmap.org/search?q=' + \
        urllib.parse.quote(address) + '&format=json&accept-language=en&zoom=3'
    response = req.get(url).json()
    return (response[0]['lat'], response[0]['lon'])


def downloadbirdimages(data):
    for bird in data:
        print(bird['comName'])
        try:
            recurseretrydownload(bird['comName'].replace(' ', '+'), 20)
        except:
            print(f'Woops! We cant get images for {bird["comName"]}')


def recurseretrydownload(key, tries):
    try:
        print(f'trying to download {key}')
        simp.Downloader().download(key, tries)
    except:
        if tries > 3:
            recurseretrydownload(key, tries-2)
        else:
            return


def generateselections(number, data):
    return [random.sample(range(len(data)), 25) for x in range(number)]

def recursiveimgread(path, pics):
    imgname = random.sample(pics, 1)[0]
    path2 = path / imgname
    thisimg = image.imread(path2.__str__())
    if np.size(thisimg,0) > 100 and np.size(thisimg,1) > 100:
        return thisimg
    else:
        pics.remove(imgname)
        return recursiveimgread(path, pics)

def generatebingo(selection, data, save):
    fstrings = [data[s]['comName'].replace(' ', '+') for s in selection]
    fig = pyplot.figure(figsize=(8, 11))
    for ind, file in enumerate(fstrings):
        name = file
        if ind != 12:
            path = pathlib.PureWindowsPath(
                __file__).parent / ('simple_images\\' + file)
            pics = [f for f in os.listdir(path) if os.path.isfile(path / f)]
            thisimg = recursiveimgread(path,pics)
        else:
            path = pathlib.PureWindowsPath(
                __file__).parent / ('freespace.jpg')
            thisimg = image.imread(path.__str__())
            name = 'Frog Space'
        fig.add_subplot(5, 5, ind+1)
        pyplot.imshow(thisimg)
        pyplot.axis('off')
        pyplot.title(name.replace('+', ' '))
    pyplot.savefig('birdo' + datetime.datetime.now().strftime('%y.%m.%d ') + save + '.png', dpi=200)
    pyplot.show()
    print('saved a bingo!')


def checkforimages(data):
    for bird in data:
        path = pathlib.PureWindowsPath(
            __file__).parent / ('simple_images\\' + bird['comName'].replace(' ', '+'))
        if len(os.listdir(path)) == 0:
            print(bird['comName'] + 'needs images')
            return False
    return True


if __name__ == '__main__':
    data = getebirddata(*getloc('ADDRESS'))
    downloadbirdimages(data)
    if checkforimages(data) is True:
        for ind, sel in enumerate(generateselections(50, data)):
            generatebingo(sel, data, str(ind))
