import os
import random, string
import pandas as pd
import numpy as np
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
           'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def randomword(length):
   return "".join(random.choices(string.ascii_letters, k=length))

with app.app_context():
    db = SQLAlchemy(app)

    class Poodle(db.Model):
        id = db.Column(db.String(24), primary_key=True)
        title = db.Column(db.String(100))
        comment = db.Column(db.Text(1000))

        def __repr__(self):
            return f'<Poodle "{self.title}">'

    class Option(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        oname = db.Column(db.String(20))
        post_id = db.Column(db.Integer, db.ForeignKey(Poodle.id))

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(20))
        post_id = db.Column(db.Integer, db.ForeignKey(Poodle.id))
        invisible = db.Column(db.Boolean, default=False)

    class Choice(db.Model):
        user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
        option_id = db.Column(db.Integer, db.ForeignKey(Option.id), primary_key=True)
        userchoice = db.Column(db.Boolean, default=False)

    db.create_all()

def add_user(poodle_id, uid, args):
    with app.app_context():
        # Add new User
        if uid == "new":
            u = User(name=args["name"], post_id=poodle_id)
            db.session.add(u)
            db.session.commit()
            choice_list = []
            for opt in db.session.query(Option).filter(Option.post_id==poodle_id).all():
                c = Choice(user_id=u.id, option_id=opt.id, userchoice="True"==args.get(str(opt.id), False))
                choice_list.append(c)
            db.session.add_all(choice_list)
            db.session.commit()
        # Edit existing User
        else:
            for opt in db.session.query(Option).filter(Option.post_id==poodle_id).all():
                c = db.session.query(Choice).filter(Choice.option_id == opt.id, Choice.user_id == uid).first()
                c.userchoice = "True"==args.get(str(opt.id), False)
            db.session.commit()

def create_poodle(title, comment="", dateoptions=[]):
    with app.app_context():
        randword = None
        while randword == None or db.session.query(Poodle.id).filter_by(id=randword).first() is not None:
            randword = randomword(24)
        new_poodle = Poodle(id=randword, title=title, comment=comment)
    
        db.session.add(new_poodle)
        db.session.commit()
        
        options = []
        for oname in dateoptions:
            o = Option(oname=oname, post_id=randword)
            options.append(o)
        u = User(name="invisible", post_id=randword, invisible=True)
        options.append(u)
        db.session.add_all(options)
        db.session.commit()
        
        # Create choices for invisible user
        addos = []
        for uid in db.session.query(User.id).filter(User.post_id==randword).first():
            for o in db.session.query(Option.id).filter(Option.post_id==randword).all():
                c = Choice(user_id=uid, option_id=o[0], userchoice=False)
                addos.append(c)
        db.session.add_all(addos)
        db.session.commit()
        return randword #ID of Poodle

def get_db(pid):
    with app.app_context():
        if db.session.query(Poodle).filter(Poodle.id == pid).first()==None:
            raise LookupError
        info = db.session.query(Poodle.title, Poodle.comment).filter(Poodle.id == pid).first()
        query = db.session.query(User.post_id, User.id, User.name, User.invisible, Option.oname, Choice.userchoice).join(User).join(Option).filter(User.post_id == pid).all()

        # read data into pandas 
        df = pd.DataFrame([r._asdict() for r in query])
        
        # pivot the results
        df_pivot_table = df.pivot(index=["id","name", "invisible"], columns="oname", values="userchoice").reset_index()
        sums = np.array(df_pivot_table.sum())
        df_pivot_table = df_pivot_table.to_dict("records")
        
        # count total of each column
        sum_row = {}
        for i, key in enumerate(df_pivot_table[0].keys()):
            sum_row[key] = sums[i]
        sum_row["name"] = "Total"
        return df_pivot_table, sum_row, info
    
def get_options(pid):
    with app.app_context():
        options = db.session.query(Option)\
            .filter(Option.post_id == pid).all()
        opts = {}
        for r in options:
             opts[r.oname] = r.id
        return opts
    
def add_option(pid, name=randomword(4)):
    with app.app_context():
        o = Option(oname=name, post_id=pid)
        db.session.add(o)
        db.session.commit()

def get_user(uid=1162):
    with app.app_context():
        query = db.session.query(Option.oname, Choice.userchoice)\
            .join(Option).filter(Choice.user_id == uid).all()
        puser = db.session.query(User.post_id, User.id, User.name).filter(User.id == uid).first()
        return puser, query