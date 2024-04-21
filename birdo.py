# -*- coding: utf-8 -*-
"""
Bird Bingo Creator
"""

import urllib.parse
import os
import datetime
import random
import pathlib
import requests as req
import ebird.api as ebirb
from simple_image_download import simple_image_download as simp
from matplotlib import pyplot, image
from dotenv import load_dotenv
import numpy as np

load_dotenv('.env')

# Load API Keys
EBIRDKEY = os.getenv('EBIRDKEY')


def getobservationsat(address: str, radius_km=2, days=30):
    """
    Retrieves observations of birds at a given address location within a 
    specified radius and timeframe.

    Parameters
    ----------
    address : str
        DESCRIPTION.
    radius_km : float, optional
        Radius in km from address to search. The default is 2.
    days : int, optional
        Number of preceeding days to search between 1 and 30. The default is 30.

    Returns
    -------
    dict
        List of observations in simple format. Only the most recent observation
        per bird species is reported.

    """
    url = 'https://nominatim.openstreetmap.org/search?q=' + \
        urllib.parse.quote(address) + '&format=json&accept-language=en&zoom=3'
    response = req.get(url, timeout = 10).json()
    return ebirb.get_nearby_observations(EBIRDKEY,
                                         response[0]['lat'],
                                         response[0]['lon'],
                                         dist=radius_km,
                                         back=days)


def downloadbirdimages(data, max_images):
    """
    Downloads images of birds based on their common names.

    Iterates through a list of bird data dictionaries and attempts to download 
    images for each bird based on its common name. If an image cannot be found 
    for a bird, the bird's common name is added to a list of birds not found.

    Parameters
    ----------
    data : list
        Output from the getobservationsat function.

    Returns
    -------
    birdnotfound : list
        list of birds failed to download.

    """
    birdnotfound = []
    for bird in data:
        print(bird['comName'])
        try:
            recurseretrydownload(bird['comName'].replace(' ', '+'), max_images)
        except:
            birdnotfound.append(bird['comName'])
    return birdnotfound


def recurseretrydownload(key, tries):
    """
    Recursively attempts to download an image based on a key using a downloader.

    This function tries to download an image based on the provided key. If the 
    download fails, it retries recursively with a reduced number of tries until 
    either the download succeeds or the number of tries is exhausted.

    Parameters
    ----------
    key : str
        Search string.
    tries : int
        number of images to attempt to download.

    Raises
    ------
    Exception
        Raised if download repeatedly fails even after all retries.

    Returns
    -------
    None.

    """
    try:
        print(f'trying to download {key}')
        simp.Downloader().download(key, tries)
    except Exception as err:
        if tries > 3:
            recurseretrydownload(key, tries-2)
        else:
            raise err


def generatebingo(selection, data, save):
    """
    Generates a bingo card with images of selected birds.

    Creates a bingo card with images of birds based on the provided selection 
    of bird data. Each selection is represented by the common name of the bird.
    The images are retrieved from the 'simple_images' directory. The function
    also includes a 'free space' image at the center of the bingo card.

    Parameters
    ----------
    selection : list
        list of 25 unique ints which determines the selected birds from data.
    data : list
        Output from the getobservationsat function.
    save : str
        string to be appended to saved file name.

    Returns
    -------
    None.

    """
    fstrings = [data[s]['comName'].replace(' ', '+') for s in selection]
    fig = pyplot.figure(figsize=(8, 11))
    for ind, file in enumerate(fstrings):
        name = file
        if ind != 12:
            path = pathlib.PureWindowsPath(
                __file__).parent / ('simple_images\\' + file)
            pics = [f for f in os.listdir(path) if os.path.isfile(path / f)]
            thisimg = recursiveimgread(path, pics)
        else:
            path = pathlib.PureWindowsPath(
                __file__).parent / ('freespace.jpg')
            thisimg = image.imread(str(path))
            name = 'Frog Space'
        fig.add_subplot(5, 5, ind+1)
        pyplot.imshow(thisimg)
        pyplot.axis('off')
        pyplot.title(name.replace('+', ' '))
    pyplot.savefig(
        'Birdo ' + datetime.datetime.now().strftime('%y.%m.%d ') + save + '.png', dpi=200)
    pyplot.show()


def recursiveimgread(path, pics):
    """
    Recursively reads an image file from the given directory path,
    ensuring that the image size is larger than the specified minimum size.

    Parameters
    ----------
    path : Path
        Directory containing image.
    pics : list
        List of image file names.

    Returns
    -------
    Image.Image
        he image object if its size is larger than the minimum size,
        otherwise recursively calls itself with a different image until a suitable image is found..

    """
    img_name = random.sample(pics, 1)[0]
    img_path = path / img_name
    thisimg = image.imread(str(img_path))
    if np.size(thisimg, 0) > 100 and np.size(thisimg, 1) > 100:
        return thisimg
    pics.remove(img_name)
    return recursiveimgread(path, pics)


def checkforimages(data):
    """
    Checks if images are available for each bird in the provided data.

    Parameters
    ----------
    data : list
        Output from the getobservationsat function.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    for bird in data:
        path = pathlib.PureWindowsPath(
            __file__).parent / ('simple_images\\' + bird['comName'].replace(' ', '+'))
        if len(os.listdir(path)) == 0:
            print(bird['comName'] + 'needs images')
            return False
    return True


def birdo(address, radius_km=2, days=30, number_bingos=20, download=True, max_images=10):
    """
    Generate bird observation bingo cards based on observations at a given address.

    Parameters
    ----------
    address : str
        The address or location to search for bird observations..
    radius_km : int, optional
        The radius in kilometers to search around the address. Default is 2.
    days : int, optional
        The number of past days to consider for bird observations. The default is 30.
    number_bingos : int, optional
        The number of bingo cards to generate. The default is 20.
    download : bool, optional
        Whether to download bird images. The default is True.
    max_images : int, optional
        The maximum number of images to download per bird. The default is 10.

    Returns
    -------
    None.

    """
    data = getobservationsat(address)
    if download:
        downloadbirdimages(data, max_images=max_images)
    if checkforimages(data) is True:
        for ind, sel in enumerate([random.sample(range(len(data)), 25)
                                   for x in range(number_bingos)]):
            generatebingo(
                sel, data, f'{address}_{radius_km}km_{days}days_number{str(ind)}')
    else:
        print('Some birds do not have images downloaded!')


if __name__ == '__main__':
    birdo('Baltimore', radius_km=20, number_bingos=1, max_images=5)
