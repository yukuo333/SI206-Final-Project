from finalproject import *
from OMDB import *
from search_videos import *
import sqlite3
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def create_omdb_table(cur,conn):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CACHE_FNAME = dir_path + '/' + "cache_movie.json"
    cur.execute("DROP TABLE IF EXISTS OMDB")
    cur.execute("CREATE TABLE OMDB (id INTEGER PRIMARY KEY, title TEXT, rating REAL,genre TEXT,year INTEGER)")
    cur.execute('SELECT name FROM Movies')
    movie_list = cur.fetchall()
    for movie in movie_list:
        if type(get_data(movie[0],CACHE_FNAME)) == list:
            movie_dt = get_data(movie[0],CACHE_FNAME)[0]
            if movie_dt['Year'] == '2020' and movie_dt['Ratings'] != None:
                #print(movie_dt)
                title = movie_dt['Title']
                rating = movie_dt['Ratings']
                genre = movie_dt['Genre']
                year = movie_dt['Year']
                cur.execute("INSERT OR IGNORE INTO OMDB (title, rating, genre,year) VALUES (?,?,?,?)",(title,rating,genre,year,))
    conn.commit()

def create_youtube_table(cur,conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Youtube (title TEXT PRIMARY KEY,likes INTEGER, dislikes INTEGER,views INTEGER)')

def insert_youtube_data(cur,conn):
    cur.execute('SELECT title FROM OMDB')
    movie_titles = cur.fetchall()
    print(movie_titles[0][0])
    x = 40 #start from 40
    for movie_title in movie_titles[x:x+25]:
        cur.execute('SELECT EXISTS(SELECT 1 FROM Youtube WHERE title = ? LIMIT 1)',(movie_title[0],))
        test = cur.fetchone()[0]
        if test == 0:
            print('hi')
            temp_movie = create_video_list(movie_title[0]+' Trailer 2020')
            title = movie_title[0]
            likes = temp_movie[0]['likes']
            dislikes = temp_movie[0]['dislikes']
            views = temp_movie[0]['viewCount']
            cur.execute('INSERT OR IGNORE INTO Youtube (title,likes,dislikes,views) VALUES (?,?,?,?)',(title,likes,dislikes,views))
    conn.commit()

def plot_rating_based_on_genre(cur,conn):
    cur.execute('SELECT * FROM OMDB')
    genre_rating = defaultdict(list)
    data = cur.fetchall()
    for datum in data:
        genre_list = datum[3].split(', ')
        for genre in genre_list:
            genre_rating[genre].append(datum[2])
    for key in genre_rating:
        genre_rating[key] = round(sum(genre_rating[key])/len(genre_rating[key]),2)

    #create folder for output text
    source_dir = os.path.dirname(__file__)
    if not os.path.exists(source_dir + '/text'):
        os.mkdir(source_dir + '/text')

    #write out to file
    filename = source_dir + '/text/average_movie_rating_by_genre.txt'
    with open(filename,'w') as f:
        for key in genre_rating:
            f.writelines(str((key,genre_rating[key]))+'\n')
    
    fig,axes = plt.subplots(figsize = (8,6))
    axes.bar(genre_rating.keys(),genre_rating.values(),align='center')
    axes.set_title('Movie Ratings based on Genre')
    axes.set_xlabel('Genre')
    axes.set_ylabel('Rating')
    axes.set_ylim(0,10)
    plt.xticks(rotation=90)
    plt.tight_layout()
    source_dir = os.path.dirname(__file__)
    if not os.path.exists(source_dir + '/plots'):
        os.mkdir(source_dir + '/plots')
    plt.savefig(source_dir + '/plots/genre_rating.png')

def plot_rating_based_on_month(cur,conn):
    month_rating = defaultdict(list)
    cur.execute('SELECT OMDB.rating,Movies.date FROM OMDB JOIN Movies ON Movies.name = OMDB.title')
    ratings_date = cur.fetchall()
    for rating in ratings_date:
        month_rating[int(int(rating[1])/100)].append(rating[0])
    for key in month_rating:
        month_rating[key] = round(sum(month_rating[key])/len(month_rating[key]),2)
    
    #create folder for output text
    source_dir = os.path.dirname(__file__)
    if not os.path.exists(source_dir + '/text'):
        os.mkdir(source_dir + '/text')

    #write out to file
    filename = source_dir + '/text/average_movie_rating_by_month.txt'
    with open(filename,'w') as f:
        for key in month_rating:
            f.writelines(str((key,month_rating[key]))+'\n')
    
    #create folder for plot
    if not os.path.exists(source_dir + '/plots'):
        os.mkdir(source_dir + '/plots')

    fig,axes = plt.subplots(figsize = (8,6))
    axes.bar(month_rating.keys(),month_rating.values(),align='center')
    axes.set_title('Movie Ratings based on Month')
    axes.set_xlabel('Month')
    axes.set_ylabel('Rating')
    axes.set_ylim(0,10)
    axes.set_xticks(np.arange(len(month_rating)+1))
    plt.tight_layout()
    source_dir = os.path.dirname(__file__)
    if not os.path.exists(source_dir + '/plots'):
        os.mkdir(source_dir + '/plots')
    plt.savefig(source_dir + '/plots/month_rating.png')

def plot_youtube_rating(cur,conn):
    cur.execute('SELECT Movies.date,Youtube.likes,Youtube.dislikes FROM Youtube JOIN Movies ON Youtube.title = Movies.name')
    youtube_ratings = cur.fetchall()
    youtube_dict = defaultdict(list)
    for rating in youtube_ratings:
        youtube_dict[str(int(int(rating[0])/100))].append(round(rating[1]/(rating[1]+rating[2]),2))
    
    for key in youtube_dict:
        youtube_dict[key] = round(sum(youtube_dict[key])/len(youtube_dict[key]),2)*10

    #create folder for output text
    source_dir = os.path.dirname(__file__)
    if not os.path.exists(source_dir + '/text'):
        os.mkdir(source_dir + '/text')

    #write out to file
    filename = source_dir + '/text/average_movie_rating_by_month_youtube.txt'
    with open(filename,'w') as f:
        for key in youtube_dict:
            f.writelines(str((key,youtube_dict[key]))+'\n')
    
    #create folder for plot
    if not os.path.exists(source_dir + '/plots'):
        os.mkdir(source_dir + '/plots')

    fig,axes = plt.subplots(figsize = (8,6))
    axes.bar(youtube_dict.keys(),youtube_dict.values(),align='center')
    axes.set_title('Movie Ratings based in each month based on likes/dislikes proportion')
    axes.set_xlabel('Month')
    axes.set_ylabel('Rating')
    axes.set_ylim(0,10)
    axes.set_xticks(np.arange(len(youtube_dict)+1))
    plt.tight_layout()
    source_dir = os.path.dirname(__file__)
    if not os.path.exists(source_dir + '/plots'):
        os.mkdir(source_dir + '/plots')
    plt.savefig(source_dir + '/plots/month_rating_youtube.png')


def main():
    cur, conn = setUpDatabase('movie_name.db')
    #create_movie_table(cur, conn)
    #create_omdb_table(cur,conn)
    #create_youtube_table(cur,conn)
    #insert_youtube_data(cur,conn)
    #plot_rating_based_on_genre(cur,conn)
    #plot_rating_based_on_month(cur,conn)
    plot_youtube_rating(cur,conn)


if __name__ == "__main__":
    main()