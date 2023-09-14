from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import User, db, Matches, Squads, Player, Teams
import bcrypt 
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:Monkey.D.Luffy@localhost/cricbuzz"
app.config['SECRET_KEY'] = "a88f6af3d02a4bff91ecd29da2b2e8ff"
jwt = JWTManager(app)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/api/admin/signup', methods=['POST'])
def register():
    usn = request.json['username']
    pwd = request.json['password']
    eml = request.json['email']
    new_user = User(
        usn=usn, 
        pwd=pwd, 
        eml=eml, 
        admin=True
        )
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "status": "Admin Account successfully created", 
        "status_code": 200, 
        "user_id": new_user.id
    })

@app.route('/api/admin/login', methods=['POST'])
def login(): 
    usn = request.json['username']
    pwd = request.json['password']

    db_user = User.query.filter_by(username=usn).first()

    if (db_user is None or not bcrypt.checkpw(pwd.encode('utf-8'), db_user.password.encode('utf-8'))):
        return jsonify({
            "status": "Incorrect username/password provided. Please retry",
            "status_code": 401
        })

    else: 
        token = create_access_token(identity=db_user.id)
        return jsonify({
            "status": "Login successful",
            "status_code": 200,
            "user_id": db_user.id,
            "access_token": token
        })

@app.route("/api/matches/<match_id>", methods=['GET'])
def match_details(match_id):
    mymatch = Matches.query.filter_by(match_id=match_id).first()
    t1 = Teams.query.filter_by(team_name=mymatch.team_1).first().team_id
    t2 = Teams.query.filter_by(team_name=mymatch.team_2).first().team_id
    sq1 = Squads.query.filter_by(team_id=t1).all()
    sq2 = Squads.query.filter_by(team_id=t2).all()
    t1_squad = []
    t2_squad = []

    for sq in sq1:
        temp = {
            "player_id": sq.player_id,
            "name": sq.name
        }
        t1_squad.append(temp)
    
    for sq in sq2:
        temp = {
            "player_id": sq.player_id,
            "name": sq.name
        }
        t2_squad.append(temp)

    return jsonify({
        "match_id": match_id,
        "team_1": mymatch.team_1,
        "team_2": mymatch.team_2,
        "date": mymatch.date, 
        "venue": mymatch.venue,
        "status": mymatch.status,
        "squads": {"team_1": t1_squad, "team_2": t2_squad}
    })


@app.route('/api/matches', methods=['POST'])
@jwt_required()
def matches_post(): 
    current_userid = get_jwt_identity()
    admin_or_not = User.query.filter_by(id=current_userid).first()
    if admin_or_not.admin: 
        t1 = request.json["team_1"]
        t2 = request.json["team_2"]
        date = request.json["date"]
        venue = request.json["venue"]
        new_match = Matches(t1=t1, t2=t2, date=date, venue=venue)
        db.session.add(new_match)
        db.session.commit() 
        return jsonify({
            "Message": "Match created successfully",
            "match_id": new_match.match_id
        })
        
    
@app.route('/api/matches', methods=['GET'])
def matches_get():
    all_matches = Matches.query.all()
    res = []
    for match in all_matches:
        temp = {
            "match_id": match.match_id,
            "team_1": match.team_1,
            "team_2": match.team_2,
            "date": match.date, 
            "venue": match.venue
        }
        res.append(temp)
    return jsonify({"matches": res})

        


@app.route('/api/teams/<team_id>/squad', methods=['POST'])
@jwt_required()
def add_player(team_id):
    name = request.json["name"]
    role = request.json["role"]
    myplayer = Player.query.filter_by(name=name).first()
    if myplayer is None: 
        abort(401)
    else:
        player_id = myplayer.player_id
    
    team_player = Squads(team_id=team_id, name=name, role=role)
    db.session.add(team_player)
    db.session.commit()

    return jsonify({ 
        "Message": "Player added to squad successfully",
        "player_id": player_id
    })


@app.route('/api/players/<player_id>/stats', methods=['GET'])
def player_stats(player_id):
    myplayer = Player.query.filter_by(player_id=player_id).first()
    return jsonify({
        "player_id": myplayer.player_id,
        "name": myplayer.name,
        "matches_played": myplayer.matches_played, 
        "runs": myplayer.runs,
        "average": myplayer.average,
        "strike_rate": myplayer.strike_rate
    })

if __name__ == '__main__':
    app.run(debug=True)