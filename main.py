import secret
from yelpapi import YelpAPI
import sqlite3
import json
import requests
import plotly.graph_objects as go
import numpy as np

yelp_id = secret.yelp_id
yelp_api = YelpAPI(secret.yelp_api)
md_api = secret.md_api
DBNAME = 'final.db'
MAPBOX_TOKEN = secret.MAPBOX_TOKEN
CACHE_NAME = "Cache_file.json"

#folloing 3 functions could be used for database rebuild
def res_database_build():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    statement = '''DROP TABLE IF EXISTS 'restaurants';'''
    c.execute(statement)
    statement = '''CREATE TABLE 'restaurants' (
            'id' INTEGER PRIMARY KEY,
            'searchid' TEXT NOT NULL,
            'name' TEXT NOT NULL,
            'url' TEXT NOT NULL,
            'closed' TEXT NOT NULL,
            'reviews' INTEGER NOT NULL,
            'rating' REAL NOT NULL,
            'address' TEXT NOT NULL,
            'city' TEXT NOT NULL,
            'zipcode' TEXT NOT NULL,
            'distance' REAL NOT NULL,
            'longitude' REAL NOT NULL,
            'latitude' REAL NOT NULL,
            'search' TEXT NOT NULL
            );
            '''

    c.execute(statement)
    conn.commit()
    conn.close()

def movie_databse_build():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    statement = '''DROP TABLE IF EXISTS 'movie_genre';'''
    c.execute(statement)

    statement = '''DROP TABLE IF EXISTS 'movie';'''
    c.execute(statement)

    statement = 'PRAGMA foreign_keys = ON;'
    c.execute(statement)

    statement = '''CREATE TABLE 'movie' (
            'movieid' INTEGER PRIMARY KEY,
            'title' TEXT NOT NULL,
            'popularity' REAL NOT NULL,
            'vote_average' REAL NOT NULL,
            'release_date' TEXT NOT NULL
            );
            '''
    c.execute(statement)

    statement = '''CREATE TABLE 'movie_genre' (
                'id' INTEGER PRIMARY KEY,
                'movieid' INTEGER NOT NULL,
                'vote_count' INTEGER NOT NULL,
                'poster_path' TEXT NOT NULL, FOREIGN KEY(movieid) REFERENCES movie(movieid)
                );
                '''
    c.execute(statement)
    conn.commit()
    conn.close()

def theater_database_build():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    statement = '''DROP TABLE IF EXISTS 'theater';'''
    c.execute(statement)
    statement = '''CREATE TABLE 'theater' (
            'id' INTEGER PRIMARY KEY,
            'theaterid' TEXT NOT NULL,
            'name' TEXT NOT NULL,
            'url' TEXT NOT NULL,
            'closed' TEXT NOT NULL,
            'reviews' INTEGER NOT NULL,
            'rating' REAL NOT NULL,
            'address' TEXT NOT NULL,
            'city' TEXT NOT NULL,
            'zipcode' TEXT NOT NULL,
            'distance' REAL NOT NULL,
            'longitude' REAL NOT NULL,
            'latitude' REAL NOT NULL,
            'search' TEXT NOT NULL
            );
            '''

    c.execute(statement)
    conn.commit()
    conn.close()

def re_yelp_results(ctype, user):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    if ctype == 'restaurant':
        arg = user.split()
        zipcode = arg[0]
        key_words = ','.join(arg[1:]).replace(',',' ')
        search = ','.join(arg[1:]).replace(',', '')
        try:
            file = open("Cache_file.json", 'r')
            contents = file.read()
            CACHE_DICTION = json.loads(contents)
            file.close()
        except:
            CACHE_DICTION = {}
        unique_url = 'yelp_api.search_query'+zipcode+search
        if unique_url in CACHE_DICTION:
            response = CACHE_DICTION[unique_url]
        else:
            response = yelp_api.search_query(term=ctype,location= str(zipcode),categories = str(key_words), limit = 20)
            CACHE_DICTION[unique_url] = response
            dumped_json = json.dumps(CACHE_DICTION)
            fw = open(CACHE_NAME, "w")
            fw.write(dumped_json)
            fw.close()

        #response = yelp_api.search_query(term=type,location= str(zipcode),categories = str(key_words), limit = 20)

        for i in range(len(response['businesses'])):
            searchid = response['businesses'][i]['id']
            name = response['businesses'][i]['name'].lower()
            url = response['businesses'][i]['url']
            closed = str(response['businesses'][i]['is_closed']).lower()
            reviews = response['businesses'][i]['review_count']
            rating = response['businesses'][i]['rating']
            address = response['businesses'][i]['location']['address1'].lower()
            city = response['businesses'][i]['location']['city'].lower()
            zipcode = response['businesses'][i]['location']['zip_code']
            distance = response['businesses'][i]['distance']
            longitude = response['businesses'][i]['coordinates']['longitude']
            latitude = response['businesses'][i]['coordinates']['latitude']
            search = search.lower()
            values = (searchid,name,url,closed,reviews,rating,address,city,zipcode,distance,longitude,latitude,search)
            statement = "INSERT INTO restaurants (searchid,name,url,closed,reviews,rating,address,city,zipcode,distance,longitude,latitude,search) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"
            c.execute(statement, values)

    conn.commit()
    conn.close()
    return

def movie_results(user):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    try:
        file = open("Cache_file.json", 'r')
        contents = file.read()
        CACHE_DICTION = json.loads(contents)
        file.close()
    except:
        CACHE_DICTION = {}
    unique_url = 'https://api.themoviedb.org/3/movie/now_playing?api_key='+md_api+'&language=en-US&page=' + str(user)
    if unique_url in CACHE_DICTION:
        response = CACHE_DICTION[unique_url]
    else:
        response = requests.get('https://api.themoviedb.org/3/movie/now_playing?api_key='+md_api+'&language=en-US&page=' + str(user))
        CACHE_DICTION[unique_url] = response.json()
        dumped_json = json.dumps(CACHE_DICTION)
        fw = open(CACHE_NAME, "w")
        fw.write(dumped_json)
        fw.close()

    content = response

    try:
        for i in range(len(content['results'])):
            movieid = content['results'][i]['id']
            title = content['results'][i]['title']
            popularity = content['results'][i]['popularity']
            vote_average = content['results'][i]['vote_average']
            release_date = content['results'][i]['release_date']
            values = (movieid,title,popularity,vote_average,release_date)
            statement = "INSERT INTO movie (movieid,title,popularity,vote_average,release_date) VALUES(?,?,?,?,?)"
            c.execute(statement, values)
            vote_count = content['results'][i]['vote_count']
            poster_path = content['results'][i]['poster_path']
            values = (movieid, vote_count,poster_path)
            statement = "INSERT INTO movie_genre (movieid, vote_count,poster_path) VALUES(?,?,?)"
            c.execute(statement, values)
    except:
        conn.commit()
        conn.close()
        return
    conn.commit()
    conn.close()
    return

def re_database_search(type,user):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    arg = user.split()
    zipcode = arg[0]
    search = ','.join(arg[1:]).replace(',', '')
    statement = 'select * from restaurants where zipcode = ' + '"' + str(zipcode) + '"' + 'and search = ' + '"' + str(search.lower()) + '"' + 'order by rating DESC limit 10'
    result = c.execute(statement).fetchall()

    count = 0
    for i in result:
        count += 1
    if count < 1 :
        return False
    return result

def resturant(type,user):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    result = re_database_search(type,user)
    if result == False:
        print('find')
        re_yelp_results(type,user)
        result = re_database_search(type,user)
    conn.commit()
    conn.close()
    return result

def theater_results(log,lag):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    search = str(log)+str(lag)
    search = search.replace('.','')
    try:
        file = open("Cache_file.json", 'r')
        contents = file.read()
        CACHE_DICTION = json.loads(contents)
        file.close()
        print('cache')
    except:
        CACHE_DICTION = {}
    unique_url = 'yelp_api.search_query' + search
    if unique_url in CACHE_DICTION:
        response = CACHE_DICTION[unique_url]
    else:
        response = yelp_api.search_query(term='theater', latitude = lag,longitude=log, limit=20)
        CACHE_DICTION[unique_url] = response
        dumped_json = json.dumps(CACHE_DICTION)
        fw = open(CACHE_NAME, "w")
        fw.write(dumped_json)
        fw.close()
    #response = yelp_api.search_query(term='theater', latitude = lag,longitude=log, limit=20)
    for i in range(len(response['businesses'])):
        theaterid = response['businesses'][i]['id']
        name = response['businesses'][i]['name'].lower()
        url = response['businesses'][i]['url']
        closed = str(response['businesses'][i]['is_closed']).lower()
        reviews = response['businesses'][i]['review_count']
        rating = response['businesses'][i]['rating']
        address = response['businesses'][i]['location']['address1'].lower()
        city = response['businesses'][i]['location']['city'].lower()
        zipcode = response['businesses'][i]['location']['zip_code']
        distance = response['businesses'][i]['distance']
        longitude = response['businesses'][i]['coordinates']['longitude']
        latitude = response['businesses'][i]['coordinates']['latitude']
        search = search
        values = (theaterid,name,url,closed,reviews,rating,address,city,zipcode,distance,longitude,latitude,search)
        statement = "INSERT INTO theater (theaterid,name,url,closed,reviews,rating,address,city,zipcode,distance,longitude,latitude,search) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"
        c.execute(statement, values)

    print('find new theater')
    conn.commit()
    conn.close()

    return

def theater_database_search(log,lag):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    search = str(log)+str(lag)
    search = search.replace('.', '')
    statement = 'select * from theater where search = ' + search + ' order by distance '
    re = c.execute(statement).fetchall()
    count = 0
    for i in re:
        count += 1
    if count < 1:
        return False
    return re

def theater(log,lag):
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    result = theater_database_search(log,lag)
    if result == False:
        theater_results(log,lag)
        result = theater_database_search(log,lag)
    conn.commit()
    conn.close()
    return result

def display_res_map(user):
    name_l = []
    log_l = []
    lat_l =[]
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    arg = user.split()
    zipcode = arg[0]
    search = ','.join(arg[1:]).replace(',', '')
    statement = 'select name,longitude,latitude from restaurants where zipcode = ' + '"' + str(zipcode) + '"' + 'and search = ' + '"' + str(search.lower()) + '"' + 'order by rating DESC limit 10'
    re = c.execute(statement).fetchall()
    for i in re:
        name_l.append(i[0])
        log_l.append(float(i[1]))
        lat_l.append(float(i[2]))
    log_mean = np.mean(log_l)
    lat_mean = np.mean(lat_l)
    fig = go.Figure(go.Scattermapbox(
        lat=lat_l,
        lon=log_l,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
        text=name_l,
    ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=MAPBOX_TOKEN,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=lat_mean,
                lon=log_mean
            ),
            pitch=0,
            zoom=15
        ),
    )

    fig.show()
    return

def display_res_hist(user):
    id_l = []
    review_l = []
    rating_l = []
    distance = []
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    arg = user.split()
    zipcode = arg[0]
    search = ','.join(arg[1:]).replace(',', '')
    statement = 'select name,reviews,rating,distance from restaurants where zipcode = ' + '"' + str(zipcode) + '"' + 'and search = ' + '"' + str(search.lower()) + '"' + 'order by rating DESC limit 10'
    re = c.execute(statement).fetchall()
    for i in re:
        id_l.append(i[0])
        review_l.append(i[1]/10)
        rating_l.append(i[2]*10)
        distance.append(float(i[3])/100)

    fig = go.Figure(data=[
        go.Bar(name='number of reviews', x=id_l, y=review_l),
        go.Bar(name='rating', x=id_l, y=rating_l),
        go.Bar(name='distance', x=id_l, y=distance)
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')
    fig.update_layout(title='Relative score for each restaurants',
                      yaxis_zeroline=False, xaxis_zeroline=False)
    fig.show()

    return

def movie_sca():
    title_l = []
    pop_l = []
    vote_l = []
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    statement = "select  title, popularity, vote_average from movie order by popularity Desc limit 10"
    re = c.execute(statement)
    for i in re:
        title_l.append(i[0])
        pop_l.append(i[1])
        vote_l.append(i[2])
    fig = go.Figure(data=go.Scatter(x=vote_l,
                                    y=pop_l,
                                    mode='markers',
                                    text=title_l))

    fig.update_layout(title='Movie vote score VS popularity',xaxis_title="vote average",
    yaxis_title="popularity",)
    fig.show()

def display_theater_map(log,lag):
    name_l = []
    log_l = []
    lat_l = []
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    search = str(log)+str(lag)
    search = search.replace('.', '')
    statement = 'select name,longitude,latitude from theater where search = ' + search + ' order by distance '
    re = c.execute(statement).fetchall()
    print("praph test")
    for i in re:
        name_l.append(i[0])
        log_l.append(float(i[1]))
        lat_l.append(float(i[2]))
    log_mean = np.mean(log_l)
    lat_mean = np.mean(lat_l)
    fig = go.Figure(go.Scattermapbox(
        lat=lat_l,
        lon=log_l,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
        text=name_l,
    ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=MAPBOX_TOKEN,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=lat_mean,
                lon=log_mean
            ),
            pitch=0,
            zoom=12
        ),
    )

    fig.show()
    return

def plan_map(real_RID,real_TID):
    name_l = []
    log_l = []
    lat_l =[]
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()
    statement = 'select name,longitude,latitude from restaurants where id =' + real_RID
    re = c.execute(statement).fetchall()
    for i in re:
        name_l.append(i[0])
        log_l.append(float(i[1]))
        lat_l.append(float(i[2]))
    statement = 'select name,longitude,latitude from theater where id =' + real_TID
    re = c.execute(statement).fetchall()
    for i in re:
        name_l.append(i[0])
        log_l.append(float(i[1]))
        lat_l.append(float(i[2]))
    log_mean = np.mean(log_l)
    lat_mean = np.mean(lat_l)
    fig = go.Figure(go.Scattermapbox(
        lat=lat_l,
        lon=log_l,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=9
        ),
        text=name_l,
    ))

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=MAPBOX_TOKEN,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=lat_mean,
                lon=log_mean
            ),
            pitch=0,
            zoom=12
        ),
    )
    fig.show()
    return

def help_text():
    print("The program will aks user if they want certain graph. Please enter 'y' to get the graph \n")
    print('\nTo start the program please start with a restaurant search \nplease enter the the zip_code followed by your restaurants preferences\nThe program will return no more than 10 results ordered by rating'
          ' \nHere is an example: "restaurant 48103 Chinese food" \n')
    print('Enter the ID number in order to show more information and enter "select" to choose the restaurant you are going to \nan example will be: \n1\nselect')
    print("\nEnter 'movie' the get no more than 10 results ordered by popularity\nEnter the MovieID number in order to show more information and poster for tha movie enter 'select' to choose the restaurant you are going to\nan example will be: \n330457\nselect")
    print("\nEnter 'theater' the get theater information nearby the restaurant order by distance \nEnter the ID number in order to show more information about the theater enter 'select' to choose the restaurant you are going to\nan example will be: \n1\nselect")
    print("\nOnce your select the resturant, movie, and theater for the weekend, you can enter 'plan' to generate the plan and map")
    return

def user_inter():
    conn = sqlite3.connect(DBNAME)
    c = conn.cursor()

    spaceer = " "
    comm = ','
    print("Wellcome to the weekend planner, if it is your first time to use this program please enter 'help' for instruction or 'exit' to terminate the program")
    text = input("please enter your command: ")
    real_MID = 'none'
    real_RID = 'none'
    real_TID = 'none'
    res_name = ''
    res_add = ''
    movie_name = ''
    theater_name = ''
    theater_add = ''



    while text != 'exit':
        if text == "help":
            help_text()
        command = text.split()
        if command[0] == 'restaurant':
            try:
                user = ','.join(command[1:]).replace(',', ' ')
                result = resturant(command[0],user)
                print('ID  Name  Num_reviews  Rating')
                for i in result:
                    print(str(i[0]) + spaceer + str(i[2])  +spaceer + str(i[5])+ spaceer + str(i[6]))
                res_map = input('Do you want to shows restaurant on the map? enter "y" or "n"')
                if res_map == 'y':
                    display_res_map(user)
                res_hist = input('Do you want to shows restaurant on the histogram? enter "y" or "n"')
                if res_hist == "y":
                    display_res_hist(user)

                get_ID = input('Enter the restaurant ID if you want to know more: ')
                while get_ID != 'select':
                    statement = "select url,address,city,zipcode,name from restaurants where id =" + get_ID
                    re = c.execute(statement)
                    for i in re:
                        print(str(i[0]))
                        print("located at:  "+ str(i[1])+comm+str(i[2])+comm+str(i[3]))
                        res_name = i[-1]
                        res_add = ','.join(i[1:4])
                    real_RID = get_ID

                    get_ID = input('If you want to know more about(enter "select" to choose your restaurant): ')

                print("\nIf your want to see a movie please enter 'movie' \n")
            except:
                print("bad input")

        if command[0] == 'movie':
            try:
                for i in range(1,6):
                    movie_results(i)
                statement = "select movieid, title, popularity, vote_average,release_date from movie order by popularity Desc limit 10"
                re = c.execute(statement)
                print('MovieID   title    popularity     vote_average    release_date')
                for i in re:
                    print(str(i[0]) + spaceer*3 + str(i[1]) + spaceer*3 + str(i[2])+ spaceer*3+ str(i[3])+ spaceer*3+ str(i[4]))
                m_graph = input('Do you want to see a graph about vote averages and popularity about the movies(enter "y"):')
                if m_graph == 'y':
                    movie_sca()
                get_MID = input('Enter the MovieID if you want to know more(enter "select" to choose your movie): ')
                while get_MID !='select':
                    statement = "select m.movieid, title, popularity, vote_average,release_date,vote_count,poster_path from movie m,movie_genre mg where m.movieid = mg.movieid and m.movieid =" + get_MID
                    re = c.execute(statement)
                    print('MovieID   title    popularity     vote_average    release_date    vote_count    poster')
                    for i in re:
                        print(str(i[0]) + spaceer * 3 + str(i[1]) + spaceer * 3 + str(i[2]) + spaceer * 3 + str(i[3]) + spaceer * 3 + str(i[4])+ spaceer * 3 + str(i[5])+ spaceer * 3 + 'http://image.tmdb.org/t/p/original/'+str(i[6]))
                        movie_name = i[1]
                    real_MID = get_MID

                    get_MID = input('Enter the MovieID if you want to know more(enter "select" to choose your movie): ')
                print("\nPlease enter 'theater' to check the near by theaters \n")
            except:
                print('bad input')

        if command[0] == 'theater':
            if real_RID == 'none':
                print("please enter search command for restaurant and select a restaurant ID")
            elif real_MID == 'none':
                print("please enter 'movie' and select a MovieID")
            else:
                try:
                    statement = "select longitude,latitude from restaurants where id ="+ str(real_RID)
                    re = c.execute(statement)
                    for i in re:
                        res_log = i[0]
                        res_lag = i[1]

                    re = theater(float(res_log) ,float(res_lag))
                    print('ID  Name  Num_reviews  Rating')
                    for i in re:
                        print(str(i[0]) + spaceer + str(i[2])  +spaceer + str(i[5])+ spaceer + str(i[6]))

                    theater_map = input('Do you want to shows theaters on the map? enter "y" or "n"')
                    if theater_map == 'y':
                        display_theater_map(res_log,res_lag)

                    get_TID = input("Enter the theater ID if you want more information(enter 'select' to choose): ")
                    while get_TID!="select":
                        statement = "select url,address,city,zipcode,name from theater where id =" + str(get_TID)
                        re = c.execute(statement)
                        for i in re:
                            print(str(i[0]))
                            print("located at:  " + str(i[1]) + comm + str(i[2]) + comm + str(i[3]))
                            theater_name = i[-1]
                            theater_add = ','.join(i[1:4])
                        real_TID = get_TID
                        get_TID = input("Enter the theater ID if you want more information(enter 'select' to choose): ")
                    print("\nPlease enter 'plan' to generate your weekend plan")
                except:
                    print('bad input')



        if command[0] == 'plan':
            if real_RID == "none":
                print('Please select a restaurant')
            elif real_MID == 'none':
                print('Please select a movie')
            elif real_TID == 'none':
                print('Please select a theater')
            else:
                print("\nGet exciting! Here is your weekend plan!\nYou will go to "+ res_name + ' located at\n'+res_add+"\nThen, you will go to "+ theater_name+ ' located at\n'+theater_add+'\n')

                print("Here is your plan Map")

                plan_map(real_RID,real_TID)

        text = input("please enter your command: ")


    # restaurant 11101 chinese food

    print('Bye and have a great weekend!')

if __name__=="__main__":
    #res_database_build()
    theater_database_build()
    user_inter()

#restaurant 11101 chinese food