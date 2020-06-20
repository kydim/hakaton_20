import sys
import json
import time
import requests
import os

from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from string import punctuation
import pymorphy2
from nltk.stem.snowball import SnowballStemmer 
import requests
from googletrans import Translator
from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from math import sqrt

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
russian_stopwords = stopwords.words("russian")
morph = pymorphy2.MorphAnalyzer()


def flatten_array(arr):
    return [item for sublist in arr for item in sublist]


def get_all_metro_stations_names(metro_stations_json=None):
    if metro_stations_json is None:
        response = requests.get('https://api.hh.ru/metro')
        metro_stations_json = json.loads(response.content)
    lines = [city['lines'] for city in metro_stations_json]
    lines = flatten_array(lines)
    stations = [line['stations'] for line in lines]
    stations = flatten_array(stations)
    names = [station['name'] for station in stations]
    return names


def get_all_metro_stations(metro_stations_json=None):
    if metro_stations_json is None:
        response = requests.get('https://api.hh.ru/metro')
        metro_stations_json = json.loads(response.content)
    lines = [city['lines'] for city in metro_stations_json]
    lines = flatten_array(lines)
    stations = [line['stations'] for line in lines]
    stations = flatten_array(stations)
    return stations


def get_nearest_stations(station, threshold = 0.06, metro_stations_json=None):
    nearest = []
    all_stations = get_all_metro_stations(metro_stations_json)
    for current_station in all_stations:
        if get_distance(current_station, station) < threshold:
            nearest.append(current_station)
    return nearest


def get_metro_stations_from_text(text, city=None, single=False, metro_stations_json=None):
    found_stations = []
    metro_stations = get_all_metro_stations(metro_stations_json)
    for station in metro_stations:
        if station['name'].lower() in text.lower():
            found_stations.append(station)
    if city is not None:
        found_stations = list(filter(lambda x: city.lower() in x['city'].lower(), found_stations))
    if single == True:
        if len(found_stations) >= 1:
            found_stations = found_stations[0]
        else:
            found_stations = None
    return found_stations


def get_nearest_stations_from_text(station, city, threshold = 0.06, metro_stations_json=None):
    station = get_metro_stations_from_text(station, city, single=True, metro_stations_json=metro_stations_json)
    print(station)
    if station is not None:
        nearest = []
        all_stations = get_all_metro_stations(metro_stations_json)
        for current_station in all_stations:
            if get_distance(current_station, station) < threshold:
                nearest.append(current_station)
        return nearest
    else:
        return []
        

def get_distance(one, two):
    return sqrt((one['lat'] - two['lat']) ** 2 + (one['lng'] - two['lng']) ** 2)


def classify_image_yandex(image_url):
  url = 'https://yandex.ru/images/search?source=collections&rpt=imageview'
  params = {'url': image_url}
  response = requests.get(url, params=params)
  print(response.url)
  soup = BeautifulSoup(response.content, 'lxml')

  soup = soup.find(class_='cbir-page-content__section_name_tags')
  json_text = soup.find(class_="Root Theme Theme_color_yandex-default Theme_size_default Theme_capacity_default Theme_space_default Theme_cosmetic_default")['data-state']
  data = json.loads(json_text)
  tags = data['tags']
  if tags is not None and len(tags) > 0: 
      return [tag['text'] for tag in tags][0]
  else:
      return None


def translate_to_russian(text):
    translator = Translator()
    result = translator.translate(text, src='en', dest='ru')
    return result.text


def classify_image_ibm(image_url, api_key):
    authenticator = IAMAuthenticator(api_key)
    visual_recognition = VisualRecognitionV3(version='2018-03-19', authenticator=authenticator)
    visual_recognition.set_service_url('https://api.us-south.visual-recognition.watson.cloud.ibm.com/instances/19c39c90-9b57-4ca0-b98a-43591ff8241f')

    result = visual_recognition.classify(url=image_url, classifier_ids=['food']).get_result()
    classes = result['images'][0]['classifiers'][0]['classes']
    #print(classes)
    newlist = sorted(classes, key=lambda x: x['score'], reverse=True)
    one_class = newlist[0]['class']
    if (one_class == 'non-food'):
        result = visual_recognition.classify(url=image_url).get_result()
        classes = result['images'][0]['classifiers'][0]['classes']
        #print(classes)
        classes = list(filter(lambda x: 'color' not in x['class'], classes))
        newlist = sorted(classes, key=lambda x: x['score'], reverse=True)
        if len(newlist) > 0:
            one_class = newlist[0]['class']
        else:
            return None
    
    return translate_to_russian(one_class)


def normalize(word, lemmatization=True, stemming=False):
    if lemmatization == True:
        word = morph.parse(word)[0].normal_form
    if stemming == True:
         stemmer = SnowballStemmer("russian")
         word = stemmer.stem(word)
    return word


def normalize_array(words, lemmatization=True, stemming=False):
    return [normalize(word, lemmatization, stemming) for word in words]


def tokenize_text(text, lemmatization=True, stemming=False):
    tokens = nltk.wordpunct_tokenize(text.lower())
    tokens = normalize_array(tokens, lemmatization, stemming)
    tokens = [token for token in tokens if token not in russian_stopwords\
              and token != " " \
              and token.strip() not in punctuation
              and not token.isnumeric()]
    return tokens


def get_categories(query):
    url = 'https://api.multisearch.io/?id=10781&lang=ru&q=7t196p'
    params = {'query': query}
    response = requests.get(url, params=params)
    data = json.loads(response.content)
    #print(data)
    if 'corrected' in data:
        return []
    categories = [node['name'] for node in data['results']['categories']]
    return categories