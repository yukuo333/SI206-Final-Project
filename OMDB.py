import json
import requests
import os
import sqlite3

apikey = 'eba65681'

def read_cache(CACHE_FNAME):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "cache_movie.json" #Global variable for file that holds the cached data
    try:
        cache_file = open(CACHE_FNAME, 'r', encoding="utf-8") # Open the file
        cache_contents = cache_file.read()  # read the file into a string
        CACHE_DICTION = json.loads(cache_contents) # And then load it into a python dictionary
        cache_file.close() # Close the file
        return CACHE_DICTION
    except:
        CACHE_DICTION = {} 
        return CACHE_DICTION

def write_cache(cache_file, cache_dict):
    with open(cache_file, 'w') as f:
        f.write(json.dumps(cache_dict))


def OMDB_API(title):
    url = f'http://www.omdbapi.com/?t={title}&apikey={apikey}&type=movie&plot=short&r=json'
    return url

def normalize_ratings(rating_list):
    sum = 0.0
    count = 0
    for rating in rating_list:
        if rating['Source'] == 'Internet Movie Database':
            sum = sum + float(rating['Value'][0:2])
            count = count + 1
        elif rating['Source'] == 'Rotten Tomatoes':
            sum = sum + float(rating['Value'].strip('%'))/10
            count = count + 1
        elif rating['Source'] == 'Metacritic':
            sum = sum + float(rating['Value'][0:2])/10
            count = count + 1
    if count == 0:
        return None
    return round(float(sum)/count,1)

def get_data(title, CACHE_FNAME):
    request_url = OMDB_API(title)
    json_dict = read_cache(CACHE_FNAME)
    if request_url in json_dict:
        # print('Using cache for ' + title)
        empty_list = []
        empty_dict = {}
        empty_dict['Title'] = json_dict[request_url]['Title']
        empty_dict['Ratings'] = normalize_ratings(json_dict[request_url]['Ratings'])
        empty_dict['Year'] = json_dict[request_url]['Year']
        empty_dict['Genre'] = json_dict[request_url]['Genre']
        empty_list.append(empty_dict)
        return empty_list
    else:
        # print('Fetching data for ' + title)
        try:
            response = requests.get(request_url)
            py_data = json.loads(response.text)
            if py_data['Response'] == 'True':
                empty_list = []
                empty_dict = {}
                json_dict[request_url] = py_data
                write_cache(CACHE_FNAME, json_dict)
                empty_dict['Title'] = json_dict[request_url]['Title']
                empty_dict['Ratings'] = normalize_ratings(json_dict[request_url]['Ratings'])
                empty_dict['Year'] = json_dict[request_url]['Year']
                empty_dict['Genre'] = json_dict[request_url]['Genre']
                empty_list.append(empty_dict)
                return empty_list
            else:
                return None
        except:
            print('Exception')
            return None
