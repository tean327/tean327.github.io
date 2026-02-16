import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
import pandas


# Configure application
app = Flask(__name__)


#Configure mail
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_USERNAME'] = "bibletherapyapp@gmail.com"
app.config['MAIL_PASSWORD'] = "sznp lily lwxu yxia"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS']= True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite databases
connectionBible = sqlite3.connect("MKJV.db", check_same_thread=False)
connection = sqlite3.connect("users.db", check_same_thread=False)
db = connection.cursor()
bibledb = connectionBible.cursor()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Configure routing
@app.route("/", methods =["GET", "POST"])
def index():
    query = ("SELECT name FROM MKJV_books")
    books = pandas.read_sql_query(query,bibledb)
    return render_template("index.html", books=books)

@app.route("/emotion", methods= ["GET","POST"])
def emotion():
    """Output verses in consideration of user input"""
    if(request.method == "GET"):
        return render_template("emotion.html")
    emotion = request.form.get("emotion")

    #SQL query in consideration of input
    if(emotion == "anxiety"):
        query = ("SELECT name, chapter, verse, text FROM MKJV_verses JOIN MKJV_books ON MKJV_books.id = book_id WHERE text LIKE ? OR text LIKE ? OR text LIKE ?", ("%anxi%"),("%worr%"),("%peace%"))
        verses = pandas.read_sql_query(query,bibledb)
    elif(emotion == "temptation"):
        verses = bibledb.execute("SELECT name, chapter, verse, text FROM MKJV_verses JOIN MKJV_books ON MKJV_books.id = book_id WHERE text LIKE ? OR text LIKE ? OR text LIKE ? OR text LIKE ?", ("%temptation%"),("%trials%"),("%tribulation%"),("%perseverance%")).fetchall()

    elif(emotion == "patience"):
        verses = bibledb.execute("SELECT name, chapter, verse, text FROM MKJV_verses JOIN MKJV_books ON MKJV_books.id = book_id WHERE text LIKE ? OR text LIKE ?", ("%patien%"),("Wait on the lord%"),).fetchall()

    elif(emotion == "joy"):
        verses = bibledb.execute("SELECT name, chapter, verse, text FROM MKJV_verses JOIN MKJV_books ON MKJV_books.id = book_id WHERE text LIKE ? OR text LIKE ?", ("%joy%"),("%rejoice%")).fetchall()

    elif(emotion == "hope"):
        verses = bibledb.execute("SELECT name, chapter, verse, text FROM MKJV_verses JOIN MKJV_books ON MKJV_books.id = book_id WHERE text LIKE ? OR text LIKE ?", ("%hope%"), ("%rejoice%")).fetchall()

    return render_template("emotion.html", emotion=emotion.upper(), verses=verses)

@app.route("/books", methods= ["GET","POST"])
def books():
    """Output verses in consideration of user input"""
    if(request.method == "GET"):
        return render_template("books.html")
    
    book = request.form.get("book")
    verses = bibledb.execute("SELECT name, chapter, verse, text FROM MKJV_verses JOIN MKJV_books ON MKJV_books.id = book_id WHERE name = ?",book).fetchall()
    return render_template("books.html",value=book, verses=verses)


#Configure login by checking if the email is registered
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure email and password was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        rows = db.execute( "SELECT * FROM users WHERE email = ?", request.form.get("email")).fetchall()

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if(request.method == "GET"):
        return render_template("register.html")
    if(request.method == "POST"):
        email = request.form.get("email")
        password = request.form.get("password")
        passwordcheck = request.form.get("confirmation")

        if (not password):
            return apology("Must provide username")

        if (passwordcheck != password):
            return apology("PASSWORDS DON'T MATCH")

        dicts = db.execute("SELECT email  FROM users").fetchall()

        for dict in dicts:
            if(not email or email == dict["email"]):
                return apology("This email is not valid")

        #Insert the new user to the database
        hashedpassword = generate_password_hash(password)
        db.execute("INSERT INTO users(email, password) VALUES(?,?)", email, hashedpassword).fetchall()
    return redirect("/login")

@app.route("/email", methods=["GET", "POST"])
def email():
    if (request.method == "GET"):
        email = db.execute("SELECT email FROM users WHERE id=?", session["user_id"]).fetchall() 
        return render_template("email.html", email=email[0]["email"])
    else:
        #Configure the email and sent it
        msg = Message(
            subject= request.form.get("subject"),
            sender=request.form.get("email"),
            body=request.form.get("text"),
            recipients=["bibletherapyapp@gmail.com"],
        )
        if( not msg.subject or not msg.sender or not msg.body or not msg.recipients):
            return apology("Must provide all the fields")

        mail.send(msg)
        return redirect("/")


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

#Close databases connection
connection.close()
connectionBible.close()
