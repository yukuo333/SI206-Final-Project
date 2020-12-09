from bs4 import BeautifulSoup
import requests
import unittest
import re
import sqlite3
import json
import os

def getLink(soup):
    tag = soup.find('a', title='List of American films of 2020 - Wikipedia')
    print(tag)
    info = "https://en.wikipedia.org"+tag.get('href')
    print("getLink worked")
    return info

def getMonth(soup, table_class):
    month_list=[]
    alist=[]
    tags = soup.find_all('table',class_=table_class)
    
    for i in tags:
        text=i.get_text()
        # remove col titles
        texts = text.split("\n")
        texts = texts[15:]
        alist.append(texts)
    
    
    alist = sum(alist, [])
    namelist=[]
    datelist=[]
    month = "00" # default: month is wrong
    date = "00" # default: month is wrong
    # month_skip_flag = 1 # 1 means month attribute is present
    # date_skip_flag = 1 # 1 means date attribute is present
    after_film_name = 0 # 0 means we haven't got to the film name yet
    
    for i in range(len(alist)):
        if alist[i].startswith("[") and alist[i].endswith("]"):
            temp_dict={}
            after_film_name = 0
            continue
        if alist[i] == "JANUARY":
            month = "01"
            continue
        elif alist[i] == "FEBRUARY":
            month = "02"
            continue
        elif alist[i] == "MARCH":
            month = "03"
            continue
        elif alist[i] == "APRIL":
            month = "04"
            continue
        elif alist[i] == "MAY":
            month = "05"
            continue
        elif alist[i] == "JUNE":
            month = "06"
            continue
        elif alist[i] == "JULY":
            month = "07"
            continue
        elif alist[i] == "AUGUST":
            month = "08"
            continue
        elif alist[i] == "SEPTEMBER":
            month = "09"
            continue
        elif alist[i] == "OCTOBER":
            month = "10"
            continue
        elif alist[i] == "NOVEMBER":
            month = "11"
            continue
        elif alist[i] == "DECEMBER":
            month = "12"
            continue
        
        if alist[i] == '' or after_film_name:
            continue
        
        if alist[i].isdigit():
            date = alist[i]
            if len(date) == 1:
                date = "0" + date
            continue
        
        if after_film_name == 0 and not (alist[i].isdigit()):
            namelist.append(alist[i])
            datelist.append(month + date)
            after_film_name = 1
    print(namelist)
    return namelist, datelist

# for i in range(len(alist)):
#     if alist[i].startswith("[") and alist[i].endswith("]"):
#         temp_dict={}
#         inner_i = 0
#         continue

#     if alist[inner_i] == "JANUARY":
#         month = "01"
#         month_skip_flag = 1
#     elif alist[inner_i] == "FEBRUARY":
#         month = "02"
#         month_skip_flag = 1
#     elif alist[inner_i] == "MARCH":
#         month = "03"
#         month_skip_flag = 1
#     else:
#         month_skip_flag = 0

#     # if inner_i == 0:
#     #     month = alist[inner_i]

#     if inner_i == 2:
#         date = alist[i]
#         if len(date) == 1:
#             date = "0" + date

#     if inner_i == 4:
#         film = alist[i]
#         temp_dict[film] = month + date
#         month_list.append(temp_dict)

#     inner_i += 1

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def create_movie_table(cur, conn):
    url="https://en.wikipedia.org/wiki/List_of_American_films_of_2020"
    r = requests.get(url, verify=False, timeout=60)
    if r.ok:
        print("request got")
        soup = BeautifulSoup(r.text,'html.parser')
        print("soup created")
        namelist, datelist = getMonth(soup, "wikitable sortable")
    else:
        print(f"Problem with getting heml from {url}")
        print(r.status_code)
    
    cur.execute("DROP TABLE IF EXISTS Movies")
    cur.execute("CREATE TABLE Movies (id INTEGER PRIMARY KEY, name TEXT, date TEXT)")
    for i in range(len(namelist)):
        cur.execute("INSERT INTO Movies (id,name,date) VALUES (?,?,?)",(i,namelist[i],datelist[i]))
    conn.commit()



def main():
    cur, conn = setUpDatabase('movie_name.db')
    create_movie_table(cur, conn)


if __name__ == "__main__":
    main()
