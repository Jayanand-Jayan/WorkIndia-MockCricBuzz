from flask_sqlalchemy import SQLAlchemy
import jwt 
import datetime 
import bcrypt 

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(256))
    email = db.Column(db.String(50))
    admin = db.Column(db.Boolean, nullable=False, default=False)
    
    def __init__(self, usn, pwd, eml, admin=False):
        self.username = usn 
        self.password = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt()) 
        self.email = eml 
        self.admin = admin 
    

class Matches(db.Model):
    __tablename__ = "matches"
    match_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_1 = db.Column(db.String(50))
    team_2 = db.Column(db.String(50))
    date = db.Column(db.String(20))
    venue = db.Column(db.String(128))
    status = db.Column(db.String(20))

    def __init__(self, t1, t2, date, venue):
        self.team_1 = t1
        self.team_2 = t2
        self.date = date 
        self.venue = venue 
        if datetime.datetime.now() > datetime.datetime.strptime(date, "%Y-%m-%d"):
            self.status = "Over"
        else:
            self.status = "Upcoming"

class Teams(db.Model):
    __tablename__ = "teams"
    team_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_name = db.Column(db.String(50))


class Squads(db.Model):
    __tablename__ = "squads"
    team_id = db.Column(db.Integer)
    player_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    role = db.Column(db.String(50))

    def __init__(self, team_id, name, role):
        self.team_id = team_id
        self.name = name
        self.role = role 



class Player(db.Model):
    __tablename__ = "player"
    player_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    matches_played = db.Column(db.Integer)
    runs = db.Column(db.Integer)
    average = db.Column(db.Float)
    strike_rate = db.Column(db.Float)

    def __init__ (self, name, mat_play=0, runs=0, avg=0, sr=0):
        self.name = name 
        self.matches_played = mat_play
        self.runs = runs
        self.average = avg
        self.strike_rate = sr
    