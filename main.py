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
    x = 143 #start from 126
    for movie_title in movie_titles[x:x+5]:
        cur.execute('SELECT EXISTS(SELECT 1 FROM Youtube WHERE title = ? LIMIT 1)',(movie_title[0],))
        test = cur.fetchone()[0]
        if test == 0:
            print(movie_title[0])
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
    genre_rating_count = {}
    data = cur.fetchall()
    for datum in data:
        genre_list = datum[3].split(', ')
        for genre in genre_list:
            genre_rating[genre].append(datum[2])
    
    for key in genre_rating:
        genre_rating_count[key] = len(key)
        genre_rating[key] = round(sum(genre_rating[key])/len(genre_rating[key]),2)
    
    #create folder for output text
    source_dir = os.path.dirname(__file__)
    if not os.path.exists(source_dir + '/text'):
        os.mkdir(source_dir + '/text')
    #create folder for output plot
    if not os.path.exists(source_dir + '/plots'):
            os.mkdir(source_dir + '/plots')
    #write out to file
    filename = source_dir + '/text/average_movie_rating_by_genre.txt'
    with open(filename,'w') as f:
        f.writelines('Movie Rating by Genre in 2020 (Overlap Included)\n')
        for key in genre_rating:
            f.writelines('The average rating for ' + key + ' genre movies in 2020 is calculated to be ' + str(genre_rating[key]) + '. (Number of movies in '+ key + ' genre: ' + str(genre_rating_count[key]) + ')\n')
    
    fig,axes = plt.subplots(figsize = (8,6))
    axes.bar(genre_rating.keys(),genre_rating.values(),align='center',color='dimgrey')
    axes.set_title('Movie Ratings by Genre (Overlap Included)')
    axes.set_xlabel('Genre')
    axes.set_ylabel('Rating')
    axes.set_ylim(0,10)
    axes.grid()
    plt.xticks(rotation=90)
    plt.tight_layout()
    source_dir = os.path.dirname(__file__)
    
    plt.savefig(source_dir + '/plots/genre_rating.png')

    fig1,axes1 = plt.subplots(figsize = (8,6))
    plt.bar(genre_rating_count.keys(),list(genre_rating_count.values()),color='lightsteelblue')
    plt.xticks(rotation = 90)
    axes1.set_xlabel('Genre')
    axes1.set_ylabel('Count')
    axes1.set_title('Movie Count by Genre (Overlap Included)')
    plt.tight_layout()
    axes1.grid()
    plt.savefig(source_dir + '/plots/genre_pie.png')

    plt.show()

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

    cur.execute('SELECT Movies.date,Youtube.likes,Youtube.dislikes FROM Youtube JOIN Movies ON Youtube.title = Movies.name')
    youtube_ratings = cur.fetchall()
    youtube_dict = defaultdict(list)
    for rating in youtube_ratings:
        youtube_dict[str(int(int(rating[0])/100))].append(round(rating[1]/(rating[1]+rating[2]),2))
    
    for key in youtube_dict:
        youtube_dict[key] = round(sum(youtube_dict[key])/len(youtube_dict[key]),2)*10

    #write out to file
    filename = source_dir + '/text/average_movie_rating_by_month.txt'
    month = ['','January','February','March','April','May','June','July','August','September','October','November','December']
    with open(filename,'w') as f:
        f.writelines('Movie Ratings by Month based on OMDB data\n')
        for key in month_rating:
            f.writelines('Movies premiered in ' + month[key] + ' have an average rating of ' + str(month_rating[key]) + '.\n')

        f.writelines('\nMovie Ratings by Month based on Youtube Likes Percentage\n')
        for key in youtube_dict:
            f.writelines('Likes percentage of movies premiered in '+ month[int(key)] + ' is ' + str(round(youtube_dict[key]*10,2)) + '%.\n')
    
    #create folder for plot
    if not os.path.exists(source_dir + '/plots'):
        os.mkdir(source_dir + '/plots')

    fig,axes = plt.subplots(figsize = (8,6))
    axes.bar(month_rating.keys(),month_rating.values(),align='center')
    axes.set_title('Movie Ratings by Month')
    axes.set_xlabel('Month')
    axes.set_ylabel('Rating')
    axes.set_ylim(0,10)
    axes.set_xticks(np.arange(len(month_rating)+1))
    plt.tight_layout()
    source_dir = os.path.dirname(__file__)
    plt.savefig(source_dir + '/plots/month_rating.png')

    fig1,axes1 = plt.subplots(figsize = (8,6))
    axes1.bar(youtube_dict.keys(),youtube_dict.values(),align='center')
    axes1.set_title('Movie Ratings by month based on likes/dislikes proportion')
    axes1.set_xlabel('Month')
    axes1.set_ylabel('Rating')
    axes1.set_ylim(0,10)
    axes1.set_xticks(np.arange(len(youtube_dict)+1))
    plt.tight_layout()
    source_dir = os.path.dirname(__file__)
    
    
    plt.savefig(source_dir + '/plots/month_rating_youtube.png')
    N = 11
    bar_width = 0.35
    ind = np.arange(N)
    fig2,axes2 = plt.subplots(figsize = (8,6))
    # print(list(month_rating.values())[0:11])
    p1 = axes2.bar(ind,list(month_rating.values())[0:11],width = bar_width,label = 'OMDB',color = 'cornflowerblue')
    p2 = axes2.bar(ind + bar_width,youtube_dict.values(),width = bar_width,label = 'Youtube',color = 'tomato')
    axes2.set_xticks(ind + bar_width/2)
    axes2.set_ylim(0,11)
    axes2.set(ylabel = 'Rating Out of 10',title = 'Average Movie Ratings by Month')
    axes2.set_xticklabels(('January','February','March','April','May','June','July','August','September','October','November'),rotation = 35)
    axes2.legend((p1[0],p2[0]),('OMDB','Youtube'))
    axes2.autoscale_view()
    axes2.grid()
    plt.savefig(source_dir + '/plots/month_rating_both_sources.png')

def main():
    cur, conn = setUpDatabase('movie_name.db')
    #create_movie_table(cur, conn)
    #create_omdb_table(cur,conn)
    #create_youtube_table(cur,conn)
    #insert_youtube_data(cur,conn)
    #plot_rating_based_on_genre(cur,conn)
    plot_rating_based_on_month(cur,conn)
    #plot_youtube_rating(cur,conn)


if __name__ == "__main__":
    main()