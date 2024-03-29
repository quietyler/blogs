from flask import Flask,redirect,render_template,request,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogs:password@localhost:8889/blogs'
app.config['SQLALCHEMY_ECHO'] = False
app.secret_key = "asdfgh"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),unique=True,nullable=False)
    password = db.Column(db.String(120),nullable=False)
    blogs = db.relationship("Blog",backref="owner")

    def __init__(self, name, password):
        self.name = name
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120),nullable=False)
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner 


@app.before_request
def require_login():
    allowed_routes=["index", "blogs", "logout", "login", "register"]
    if "user" not in session and request.endpoint not in allowed_routes:
        return redirect('/log-in')

@app.route('/')
def index():
    users = User.query.all()
    return render_template ("index.html", users=users)
    

@app.route('/blogs')
def blogs():
    
    blogs = Blog.query.all()
    if request.args.get("id") is not None:
        blogs = Blog.query.filter_by(id=request.args['id']).all()
    elif request.args.get("user") is not None:
        blogs = Blog.query.filter_by(owner_id = request.args.get('user'))
    return render_template ("blogs.html",blogs=blogs)

@app.route('/new_blog',methods=['GET','POST'])
def new_blog():
 
    if request.method == 'POST':
        title=request.form["title"]
        body=request.form["body"]
        title_error = ''
        body_error = ''
        user = User.query.filter_by(name = session['user']).first()

        if len(title)==0:
            title_error = "Please enter title"

        if len(body)==0:
            body_error = "Please enter body"

        if title_error or body_error:
            return render_template('new_blog.html',title = title,body=body,title_error=title_error,body_error=body_error)
        
        new_blog = Blog(title,body,user)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blogs')
    return render_template("new_blog.html" )

@app.route('/log-in',methods=['GET',"POST"])
def login():

    if request.method == 'POST':
        isUser = User.query.filter_by(name = request.form['user']).first()
        password = request.form['password']
        username_error = ''
        password_error = ''

        if isUser is None:
            username_error = "user does not exist."
        if isUser and isUser.password != password:
            password_error = 'Password is incorrect'
        if username_error or password_error:
            return render_template('log-in.html',username = request.form['user'],user_error = username_error,password_error = password_error)

        if isUser and isUser.password == request.form['password']:
            print("This ran")
            session['user'] = request.form['user']
            return redirect('/new_blog')
    return render_template('/log-in.html')

@app.route('/log-out')
def logout():
    del session['user']
    return redirect('/')


@app.route("/register", methods=["GET", "POST"])
def register(): 
    if request.method == "POST":
        username=request.form["username"]
        password=request.form["password"]
        verifypassword=request.form["verifypassword"]

        Username_Error=""
        Password_Error=""
        Valid_Error=""

        if len(username)<3 or len(username)>=20:
            Username_Error="Please input valid username."

        if len(password)<3 or len(password)>=20:
            Password_Error="Please input valid password."
        
        elif password!=verifypassword:
            Valid_Error="Passwords doesn't match."

        if not Username_Error and not Password_Error and not Valid_Error:
            existing_user = User.query.filter_by(name=username).first()
            if existing_user is not None:
                username_error = "There is already somebody with that username"
            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['user'] = username
                print(session['user'])
                return redirect("/new_blog")
        else:
            return render_template("register.html", username=username, user_error=Username_Error, password_error=Password_Error, verify_error=Valid_Error)

    return render_template("register.html", title= "Register for this Blog")

if __name__ == "__main__":
    app.run()
