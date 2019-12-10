import main
import unittest
import sqlite3
class TestStringMethods(unittest.TestCase):

    def test_access(self):
        conn = sqlite3.connect(main.DBNAME)
        c = conn.cursor()
        self.assertTrue(c,True)                      #1
        statement = 'SELECT EXISTS (SELECT * FROM restaurants);'
        res = c.execute(statement).fetchall()
        self.assertEqual(res[0][0],1)                #2
        statement = 'SELECT EXISTS (SELECT * FROM movie);'
        res = c.execute(statement).fetchall()
        self.assertEqual(res[0][0], 1)               #3
        statement = 'SELECT EXISTS (SELECT * FROM movie_genre);'
        res = c.execute(statement).fetchall()
        self.assertEqual(res[0][0], 1)               #4
        statement = 'SELECT EXISTS (SELECT * FROM theater);'
        res = c.execute(statement).fetchall()
        self.assertEqual(res[0][0], 1)               #5
        conn.commit()
        conn.close()

    def test_storage(self):
        conn = sqlite3.connect(main.DBNAME)
        c = conn.cursor()
        value_test = []
        value_back = []
        value = ('testsearchid', 'test restaurant', 'www.test.com',"false",999, 9.9,'test st','test city', 'test zipcode',999.9,99.9,99.9,'test search')
        statement = "INSERT INTO restaurants (searchid,name,url,closed,reviews,rating,address,city,zipcode,distance,longitude,latitude,search) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"
        c.execute(statement,value)
        statement = 'select * from restaurants where searchid = "testsearchid" '
        res = c.execute(statement).fetchall()
        for i in value:
            value_test.append(str(i))
        for j in res[0][1:]:
            value_back.append(str(j))
        self.assertEqual(value_back, value_test)   #1
        statement = 'DELETE from restaurants where searchid = "testsearchid" '
        c.execute(statement)
        statement = 'SELECT EXISTS (SELECT * FROM restaurants where searchid = "testsearchid");'
        res = c.execute(statement).fetchall()
        self.assertEqual(res[0][0],0)              #2

        value_test = []
        value_back = []
        value = ('testtheaterid', 'testtheater', 'www.test.com',"false",999, 9.9,'test st','test city', 'test zipcode',999.9,99.9,99.9,'test search')
        statement = "INSERT INTO theater (theaterid,name,url,closed,reviews,rating,address,city,zipcode,distance,longitude,latitude,search) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"
        c.execute(statement,value)
        statement = 'select * from theater where theaterid = "testtheaterid" '
        res = c.execute(statement).fetchall()
        for i in value:
            value_test.append(str(i))
        for j in res[0][1:]:
            value_back.append(str(j))
        self.assertEqual(value_back, value_test)   #3
        statement = 'DELETE from theater where theaterid = "testtheaterid" '
        c.execute(statement)
        statement = 'SELECT EXISTS (SELECT * FROM theater where theaterid = "testtheaterid");'
        res = c.execute(statement).fetchall()
        self.assertEqual(res[0][0],0)              #4

        value_test = []
        value_back = []
        value = (9999,'test',99.99,9.9,'testdate')
        statement = "INSERT INTO movie (movieid,title,popularity,vote_average,release_date) VALUES(?,?,?,?,?)"
        c.execute(statement,value)
        statement = 'select * from movie where movieid = 9999 '
        res = c.execute(statement).fetchall()
        for i in value:
            value_test.append(str(i))
        for j in res[0]:
            value_back.append(str(j))
        self.assertEqual(value_back, value_test)   #5
        statement = 'DELETE from movie where movieid = 9999 '
        c.execute(statement)



        conn.commit()
        conn.close()

    def test_processing(self):
        conn = sqlite3.connect(main.DBNAME)
        c = conn.cursor()
        statement = 'select count(id) from restaurants'
        res = c.execute(statement).fetchall()
        self.assertGreaterEqual(res[0][0],100) #1
        statement = 'select avg(rating) from restaurants'
        res = c.execute(statement).fetchall()
        self.assertGreaterEqual(res[0][0],3)   #2
        statement = 'select avg(distance) from restaurants'
        res = c.execute(statement).fetchall()
        self.assertLessEqual(res[0][0],40000)  #3
        statement = 'select COUNT(DISTINCT movieid) from movie'
        res1 = c.execute(statement).fetchall()
        statement = 'select count(movieid) from movie'
        res2 = c.execute(statement).fetchall()
        self.assertEqual(res1,res2)            #4
        statement = 'SELECT EXISTS (select sum(popularity) from movie);'
        res = c.execute(statement).fetchall()
        self.assertEqual(res[0][0],1)          #5

if __name__ == '__main__':
    unittest.main()