import smtplib
import dns.resolver
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, TextAreaField, validators
from passlib.hash import sha512_crypt
from functools import wraps
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "STAR"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "your username"
app.config["MYSQL_PASSWORD"] = "your password"
app.config["MYSQL_DB"] = "article"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)


class RegisterForm(Form):
    name = StringField("Name: ", validators=[
        validators.Length(min=1, max=100),
        validators.DataRequired("Please enter a name")
    ])
    surname = StringField("Surname: ", validators=[
        validators.Length(min=1, max=100),
        validators.DataRequired("Please enter a surname")
    ])
    email = StringField("Email: ", validators=[
        validators.Length(min=7, max=225),
        validators.Email(message="Please enter a valid email"),
        validators.DataRequired("Please enter an email"),
    ])
    password = PasswordField("Password: ", validators=[
        validators.Length(min=5, max=100),
        validators.EqualTo("confirm", message="Passwords are not equal"),
        validators.DataRequired("Please enter a password")
    ])
    confirm = PasswordField("Repeat password: ")


class LoginForm(Form):
    email = StringField("Email: ")
    password = PasswordField("Password: ")


class ArticleForm(Form):
    title = StringField("Title: ", validators=[
        validators.Length(min=1, max=225),
        validators.DataRequired("Please enter title")
    ])
    content = TextAreaField("Content: ", validators=[
        validators.Length(min=10),
        validators.DataRequired("Please enter content")
    ])


class CommentForm(Form):
    comment = StringField("Comment: ", validators=[
        validators.Length(max=300),
        validators.DataRequired("You can't comment an empity text")
    ])


def check_email_exist(email):  # Check emil is exist or not witth help of the SMPT server
    try:
        # Get domain from email
        domain = email.split('@')[1]

        # Get MX record for the domain
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)

        # SMTP lib setup (use default port)
        server = smtplib.SMTP()
        server.set_debuglevel(0)

        # SMTP Conversation
        server.connect(mx_record)
        server.helo(server.local_hostname)  # server.local_hostname(Get local server hostname)
        server.mail('me@domain.com')  # Must be a valid email address
        code, message = server.rcpt(email)
        server.quit()

        # Assume 250 as Success
        if code == 250:
            return True
        else:
            return False

    except Exception:
        return False


def send_message_to_email(receiver_email, title, body):
    # Email details
    # SMTP server details
    sender_email = "flaskapp2004@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    password = "gacgbjeapyaxifla"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = title
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception:
        server.quit()
        return False


def login_required(f):  # This is used for to prevent unauthorized access
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login in order do this action", "error")
            return redirect(url_for("login"))
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = sha512_crypt.hash(form.password.data)  # Add password to db in a way that it can not be readed
        if check_email_exist(email):
            cursor = mysql.connection.cursor()
            sql1 = "select * from users where email = %s"
            result = cursor.execute(sql1, (email, ))
            print("result: ", result)
            if result == 0:
                sql2 = "Insert into users(name, surname, email, password) values(%s, %s, %s, %s)"
                cursor.execute(sql2, (name, surname, email, password))
                mysql.connection.commit()
                cursor.close()
                flash("You successfully entered", "success")
                title = "Welcome"
                body = "Welcome to Ali Abasgulizada's article web site"
                send_message_to_email(email, title, body)
                return redirect(url_for("login"))
            else:  # Check if user is aleady exist
                cursor.close()
                flash("Email is already taken", "error")
                return redirect(url_for("register"))
        flash("Email is not exist", "error")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        email = form.email.data
        password = form.password.data
        cursor = mysql.connection.cursor()
        sql1 = "Select * from users where email = %s"
        result = cursor.execute(sql1, (email, ))
        if result > 0:
            user = cursor.fetchone()
            cursor.close()
            if sha512_crypt.verify(password, user["password"]):
                session["logged_in"] = True
                session["name"] = user["name"]
                session["surname"] = user["surname"]
                session["email"] = email
                flash(f"Welcome {user["name"]} {user["surname"]}", "success")
                return redirect(url_for("index"))
            else:
                flash("Password is wrong", "error")
                return redirect(url_for("login"))
        else:
            cursor.close()
            flash("Your email is wrong", "error")
            return redirect(url_for("login"))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash("You successfully logout", "success")
    return redirect(url_for("index"))


@app.route("/control_panel")
@login_required
def control_panel():
    cursor = mysql.connection.cursor()
    sql = "Select * from articles where email = %s"
    result = cursor.execute(sql, (session["email"], ))
    if result > 0:
        all_articles = cursor.fetchall()
        cursor.close()
        return render_template("control_panel.html", all_articles=all_articles)
    cursor.close()
    return render_template("control_panel.html")


@app.route("/add_article", methods=["GET", "POST"])
@login_required
def add_article():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        cursor = mysql.connection.cursor()
        sql = "Insert into articles(title, content, email) values (%s, %s, %s)"
        cursor.execute(sql, (title, content, session["email"]))
        mysql.connection.commit()
        cursor.close()
        flash("Article added successfully", "success")
        return redirect(url_for("control_panel"))
    return render_template("add_article.html", form=form)


@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sql = "Select * from articles"
    result = cursor.execute(sql)
    if result > 0:
        all_articles = cursor.fetchall()
        cursor.close()
        return render_template("articles.html", all_articles=all_articles)
    cursor.close()
    return render_template("articles.html")


@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()
    sql = "Select * from articles where id = %s"
    result = cursor.execute(sql, (id, ))
    if result > 0:
        form = CommentForm(request.form)
        one_article = cursor.fetchone()
        sql2 = "Select * from comments where article_id = %s"
        result2 = cursor.execute(sql2, (id, ))
        if result2 > 0:
            comments = cursor.fetchall()
            cursor.close()
            return render_template("article.html", one_article=one_article, form=form, comments=comments)
        cursor.close()
        return render_template("article.html", one_article=one_article, form=form)
    cursor.close()
    flash("Article doesn't exist", "warning")
    return redirect(url_for("articles"))


@app.route("/comment/<string:id>", methods=["GET", "POST"])
@login_required
def comment(id):
    if request.method == "POST":
        form = CommentForm(request.form)
        if form.validate():
            content = form.comment.data
            cursor = mysql.connection.cursor()
            sql = "Insert into comments (article_id, email, content) values (%s, %s, %s)"
            cursor.execute(sql, (id, session["email"], content))
            mysql.connection.commit()
            sql2 = "Select * from articles where id = %s"
            cursor.execute(sql2, (id, ))
            one_article = cursor.fetchone()
            send_message_to_email(one_article["email"], session["email"] + " commented on your article with name: " + one_article["title"], content)
            cursor.close()
            flash("Comment added successfully", "success")
        else:
            flash("You must write something in comment", "warning")
    return redirect(url_for("article", id=id))


@app.route("/edit/<string:id>", methods=["GET", "POST"])
@login_required
def update(id):
    cursor = mysql.connection.cursor()
    if request.method == "GET":
        sql = "Select * from articles where id = %s"
        result = cursor.execute(sql, (id, ))
        if result > 0:
            one_article = cursor.fetchone()
            form = ArticleForm()
            form.title.data = one_article["title"]
            form.content.data = one_article["content"]
            cursor.close()
            return render_template("update.html", form=form)
        cursor.close()
        flash(session['name'] + " " + session['surname'] + " does not own this article", "error")
        return redirect(url_for("control_panel"))
    form = ArticleForm(request.form)
    newTitle = form.title.data
    newContent = form.content.data
    sql = "Update articles set title = %s, content = %s where id = %s"
    cursor.execute(sql, (newTitle, newContent, id))
    mysql.connection.commit()
    cursor.close()
    flash("Article updated successfully", "success")
    return redirect(url_for("control_panel"))


@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    sql1 = "Select * from articles where id = %s"
    result = cursor.execute(sql1, (id, ))
    if result > 0:
        sql2 = "Delete from articles where id = %s"
        cursor.execute(sql2, (id, ))
        sql3 = "Delete from comments where article_id = %s"
        cursor.execute(sql3, (id, ))
        mysql.connection.commit()
        cursor.close()
        flash("Article deleted successfully", "success")
        return redirect(url_for("control_panel"))
    cursor.close()
    flash(session["name"] + " " + session["surname"] + " does not own this article", "error")
    return redirect(url_for("control_panel"))


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        keyword = request.form.get("keyword")
        sql = "Select * from articles where title like %s"
        result = cursor.execute(sql, ('%' + keyword + '%',))
        if result > 0:
            all_articles = cursor.fetchall()
            cursor.close()
            return render_template("articles.html", all_articles=all_articles)
        cursor.close()
        flash("Article is not found", "warning")
        return redirect(url_for("articles"))
    return redirect(url_for("articles"))


if __name__ == "__main__":
    app.run(debug=True)  # Change to True if you want to debug or check app
