from flask import Flask, request, Response
import mariadb
import json
import dbcreds
import secrets
import datetime


app = Flask(__name__)

def connect():
    return mariadb.connect(
        user = dbcreds.user,
        password = dbcreds.password,
        host = dbcreds.host,
        port = dbcreds.port,
        database = dbcreds.database
    )

# ...........................End Points For Users.................................................
@app.route('/api/users', methods=['GET','POST', 'PATCH', 'DELETE'])

def users():
    if request.method == 'GET':
        conn = None
        cursor = None
        user = None
        users = None
        userId = request.args.get("id")
        try:
            conn = connect()
            cursor = conn.cursor()
            if (userId != None):
                cursor.execute("SELECT * FROM user WHERE id = ?", [userId])
            else:    
                cursor.execute("SELECT * FROM user")
            users = cursor.fetchall()
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (users != None):
                results = []
                for user in users:
                    result = {
                        "userId": user[0],
                        "email": user[1],
                        "username": user[2],
                        "bio": user[3],
                        "birthdate": user[4]
                    }
                    results.append(result)
                return Response(
                    json.dumps(results, default=str),
                    mimetype = "application/json",
                    status=200
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 
    elif request.method == 'POST':
        conn = None
        cursor = None
        user = None
        results = None
        email = request.json.get("email")
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        password = request.json.get("password")

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user(email, username, bio, birthdate, password) VALUES(?, ?, ?, ?, ?)", [email, username, bio, birthdate, password])
            results = cursor.rowcount 
            if results == 1:
                loginToken = secrets.token_hex(16)
                userId = cursor.lastrowid
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES (?, ?)", [userId, loginToken])
                conn.commit()
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                    user_data = {
                        "userId": userId,
                        "email": email,
                        "username": username,
                        "bio": bio,
                        "birthdate": birthdate,
                        "loginToken": loginToken
                    }
                    return Response(
                       json.dumps(user_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        results = None
        email = request.json.get("email")
        username = request.json.get("username")
        bio = request.json.get("bio")
        birthdate = request.json.get("birthdate")
        password = request.json.get("password")
        loginToken = request.json.get("loginToken")

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT userId FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchone() 
            print(target)
            if target:
                if (email != "" and email != None):
                    cursor.execute("UPDATE user SET email = ? WHERE id = ?", [email, target[0]])
                if (username != "" and username != None):
                    cursor.execute("UPDATE user SET username = ? WHERE id = ?", [username, target[0]])
                if (bio != "" and bio != None):
                    cursor.execute("UPDATE user SET bio = ? WHERE id = ?", [bio, target[0]])
                if (birthdate != "" and birthdate != None):
                    cursor.execute("UPDATE user SET birthdate = ? WHERE id = ?", [birthdate, target[0]])
                if (password != "" and password != None):
                    cursor.execute("UPDATE user SET password = ? WHERE id = ?", [password, target[0]])
                conn.commit()
                results = cursor.rowcount
                cursor.execute("SELECT * FROM user WHERE id = ?", [target[0]]) 
                user = cursor.fetchall()  
                print(user)                 
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results != None):
                    user_data = {
                        "userId": target[0],
                        "email": user[0][1],
                        "username": user[0][2],
                        "bio": user[0][3],
                        "birthdate": user[0][4],
                    }
                    return Response(
                       json.dumps(user_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        results = None
        password = request.json.get("password")
        loginToken = request.json.get("loginToken")

        try:
            conn = connect()
            cursor = conn.cursor()   
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            user = cursor.fetchall()
            print(user, password)
            userId = user[0][0]
            if user[0][1] == loginToken:
                cursor.execute("DELETE FROM user WHERE id = ? AND password = ?", [userId, password])
                conn.commit()
                results = cursor.rowcount
                print(results)
            else: 
                return Response(
                    "invalid password",
                    mimetype="text/html",
                    status=500
                )    
            
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                return Response(
                    "Deleted!...",
                    mimetype = "text/html",
                    status=204
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )              





# # ...........................End Points For Login.................................................
@app.route('/api/login', methods=['POST', 'DELETE'])

def login():
    if request.method == 'POST':
        conn = None
        cursor = None
        userId = None
        results = None
        email = request.json.get("email")
        password = request.json.get("password")

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, username, bio, birthdate, password FROM user WHERE email = ? AND password = ?", [email, password])
            userId = cursor.fetchall()
            loginToken = secrets.token_hex(16)
            print(userId) 
            print(loginToken)
            if (userId != None):
                cursor.execute("INSERT INTO user_session(userId, loginToken) VALUES (?, ?)", [userId[0][0], loginToken])
                conn.commit()
                results = cursor.rowcount
            else:
                print("wrong data")    
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                    user_data = {
                        "userId": userId[0][0],
                        "email": userId[0][1],
                        "username": userId[0][2],
                        "bio": userId[0][3],
                        "birthdate": userId[0][4],
                        "loginToken": loginToken
                    }
                    return Response(
                       json.dumps(user_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        results = None
        loginToken = request.json.get("loginToken")

        try:
            conn = connect()
            cursor = conn.cursor()   
            cursor.execute("DELETE FROM user_session WHERE loginToken = ?", [loginToken])  
            conn.commit()
            results = cursor.rowcount  
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                return Response(
                    "logout.....!",
                    mimetype = "text/html",
                    status=204
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 





# # ...........................End Points For Follows.................................................
# @app.route('/api/follows', methods=['GET','POST', 'DELETE'])
# def follows():
# # ...........................End Points For Followers.................................................
# @app.route('/api/followers', methods=['GET'])
# def followers():
# # ...........................End Points For Tweets.................................................
@app.route('/api/tweets', methods=['GET','POST', 'PATCH', 'DELETE'])
def tweets():
    if request.method == 'GET':
        conn = None
        cursor = None
        tweet_data = None
        results = None
        userId = request.args.get("userId")
        try:
            conn = connect()
            cursor = conn.cursor()
            if (userId != "" and userId != None):
                cursor.execute("SELECT tweet.id, tweet.userId, user.username, tweet.content, tweet.createdAt FROM tweet JOIN user ON tweet.userId = user.id WHERE user.id = ?", [userId])
            else:    
                cursor.execute("SELECT tweet.id, tweet.userId, user.username, tweet.content, tweet.createdAt FROM tweet JOIN user ON tweet.userId = user.id")
            results = cursor.fetchall()
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results != None):
                tweets = []
                for result in results:
                    tweet = {
                        "tweetId": result[0],
                        "userId": result[1],
                        "username": result[2],
                        "content": result[3],
                        "createdAt": result[4],
                    }
                    tweets.append(tweet)
                return Response(
                    json.dumps(tweets, default=str),
                    mimetype = "application/json",
                    status=200
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 
    elif request.method == 'POST':
        conn = None
        cursor = None
        results = None
        tweetId = None
        content = request.json.get("content")
        createdAt = request.json.get("createdAt")
        loginToken = request.json.get("loginToken")
        

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT user_session.userId, user.username FROM user_session JOIN user ON user_session.userId = user.id WHERE user_session.loginToken = ?", [loginToken])
            target = cursor.fetchall()
            print(target)
            if (len(target) == 1):
                cursor.execute("INSERT INTO tweet(userId, content, createdAt) VALUES (?, ?, ?)", [target[0][0], content, createdAt])
                conn.commit()
                tweetId = cursor.lastrowid 
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (tweetId != None):
                    tweet_data = {
                        "tweetId": tweetId,
                        "userId": target[0][0],
                        "username": target[0][1],
                        "content": content,
                        "createdAt": createdAt
                    }
                    return Response(
                       json.dumps(tweet_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 
    elif request.method == 'PATCH':
        conn = None
        cursor = None
        results = None
        newTweet_data = None
        tweetId = request.json.get("tweetId")
        content = request.json.get("content")
        loginToken = request.json.get("loginToken")

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchall() 
            print(target)
            if target[0][1] == loginToken:
                cursor.execute("UPDATE tweet SET content = ? WHERE id = ?", [content, tweetId])
                conn.commit()
            results = cursor.rowcount
            print(results)
            cursor.execute("SELECT * FROM tweet WHERE id = ?", [tweetId]) 
            new_tweet = cursor.fetchall()  
            print(new_tweet)                 
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                    newTweet_data = {
                        "tweetId": new_tweet[0][0],
                        "content": new_tweet[0][1]
                    }
                    return Response(
                       json.dumps(newTweet_data, default=str),
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        results = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")

        try:
            conn = connect()
            cursor = conn.cursor()   
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchall()
            print(target)
            if target[0][1] == loginToken:
                cursor.execute("DELETE FROM tweet WHERE id = ?", [tweetId])
                conn.commit()
                results = cursor.rowcount
                print(results)  
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results == 1):
                return Response(
                    "Deleted!...",
                    mimetype = "text/html",
                    status=204
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )              






# # ...........................End Points For Tweet-likes.................................................
@app.route('/api/tweet_likes', methods=['GET','POST', 'DELETE'])
def tweet_likes():
    if request.method == 'GET':
        conn = None
        cursor = None
        tweet_likes = None
        tweetId = request.args.get("tweetId")
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT tweet_like.tweetId, tweet_like.userId, user.username FROM tweet_like JOIN user ON tweet_like.userId = user.id WHERE tweet_like.tweetId = ?", [tweetId])
            tweet_likes = cursor.fetchall()
            print(tweet_likes)
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (tweet_likes != None):
                results = []
                for tweet_like in tweet_likes:
                    likes_data = {
                        "tweetId": tweet_like[0],
                        "userId": tweet_like[1],
                        "username": tweet_like[2]
                    }
                    results.append(likes_data)
                return Response(
                    json.dumps(results, default=str),
                    mimetype = "application/json",
                    status=200
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 
    elif request.method == 'POST':
        conn = None
        cursor = None
        results = None
        tweetId = request.json.get("tweetId")
        loginToken = request.json.get("loginToken")
        

        
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            new_like = cursor.fetchall()
            print(new_like)
            if (new_like[0][1] == loginToken):
                cursor.execute("INSERT INTO tweet_like(tweetId, userId) VALUES (?, ?)", [tweetId, new_like[0][0]])
                conn.commit()
                results = cursor.rowcount
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results != None):
                    return Response(
                       "you liked this tweet!..",
                       mimetype = "application/json",
                       status=200
                    ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                ) 
    elif request.method == 'DELETE':
        conn = None
        cursor = None
        results = None
        loginToken = request.json.get("loginToken")
        tweetId = request.json.get("tweetId")

        try:
            conn = connect()
            cursor = conn.cursor()   
            cursor.execute("SELECT * FROM user_session WHERE loginToken = ?", [loginToken])
            target = cursor.fetchall()
            print(target)
            if target[0][1] == loginToken:
                cursor.execute("DELETE FROM tweet_like WHERE tweetId = ? AND userId = ?", [tweetId, target[0][0]])
                conn.commit()
                results = cursor.rowcount
                print(results)  
        except Exception as ex:
            print("error")
            print(ex)
        finally:
            if (cursor != None):
                cursor.close()
            if (conn != None):
                conn.rollback()
                conn.close()
            if (results != None):
                return Response(
                    "You unlike this tweet!..",
                    mimetype = "text/html",
                    status=204
                ) 
            else: 
                return Response(
                    "something wrong..",
                    mimetype="text/html",
                    status=500
                )  






























# # ...........................End Points For Comments.................................................
# @app.route('/api/comments', methods=['GET','POST', 'PATCH', 'DELETE'])
# def comments():
# # ...........................End Points For Comment-likes.................................................
# @app.route('/api/comment-likes', methods=['GET','POST', 'DELETE'])
# def comment-likes():
