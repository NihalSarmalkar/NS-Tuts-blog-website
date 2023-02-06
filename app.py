from flask import Flask, render_template,request,session,redirect,flash
import json
from flask.app import Flask
from flask.globals import request
from flask import request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import os

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server=True
app=Flask(__name__)



if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
    
db=SQLAlchemy(app)

app.secret_key="super_secret_key"
app.config['UPLOAD_FOLDER'] = params['upload_location']

class Contacts(db.Model):
    
    sno=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), nullable=False)
    phone_num=db.Column(db.String(12), nullable=False)
    msg=db.Column(db.String(120), nullable=False)
   
    email=db.Column(db.String(20), nullable=False) 

class Posts(db.Model):
    
    sno=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(80), nullable=False)
    slug=db.Column(db.String(21), nullable=False)
    content=db.Column(db.String(120), nullable=False)
    categories=db.Column(db.String(21), nullable=True)
    content3=db.Column(db.String(120), nullable=False)
    tagline=db.Column(db.String(120), nullable=False)
    img_file=db.Column(db.String(12),nullable=True)
    img_file_s=db.Column(db.String(12),nullable=True)



@app.route("/")
def home():
    flash("Watch our new video ! ","success")
    posts=Posts.query.filter_by().all()
    categories_list=["Computer Science","Gadgets","Tutorials"]
    
    
    return render_template('index.html',params=params,posts=posts,categories=categories_list)

@app.route("/blog")
def blog():
    if(request.args):
        args = request.args
        print(args['category'])
        posts=Posts.query.filter_by(categories=args['category']).all()
        postlist=Posts.query.filter_by().all()
        thiisset=set()
        for i in postlist:
            thiisset.add(i.categories)
   
        return render_template('blog.html',params=params,posts=posts,postlist=postlist,categories=list(thiisset))
    else:
        posts=Posts.query.filter_by().all()
        thiisset=set()
        for i in posts:
            thiisset.add(i.categories)
      
        return render_template('blog.html',params=params,posts=posts,categories=list(thiisset))


@app.route("/contact", methods=['GET','POST'])
def contact():
    
    if(request.method=='POST'):
        #add entry to database
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message= request.form.get('message')

        entry= Contacts(name=name,phone_num=phone,msg=message,email=email)
        db.session.add(entry)
        db.session.commit()
        
        flash("Message submited successfully ! ","success")

    
    



        




    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projectpage')
def projectpage_1():
    return render_template('projectpage.html')

@app.route('/privacy-policy')
def pp():
    return render_template('pp.html')

@app.route('/terms-and-conditions')
def tandc():
    return render_template('tandc.html')

@app.route('/projectpage_2')
def projectpage_2():
    return render_template('projectpage1.html')

@app.route('/projectpage_3')
def projectpage_3():
    return render_template('projectpage2.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']==params['admin_user']:
        if request.method=='POST':
            box_title=request.form.get('title')
            tagline=request.form.get('tagline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            categories=request.form.get('categories')

            content3=request.form.get('content3')
            img_file=request.form.get('img_file')
            img_file_s=request.form.get('img_file_s')

            if sno=='0':

                post=Posts(title=box_title,slug=slug,tagline=tagline,content=content,categories=categories,content3=content3,img_file=img_file,img_file_s=img_file_s)
                db.session.add(post)
                db.session.commit()
                
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.categories=categories

                post.content3=content3
                post.tagline=tagline
         
                post.img_file=img_file
                post.img_file_s=img_file_s
                db.session.commit()
                return redirect('/edit/'+sno)

        post=Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno=sno)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user']==params['admin_user']:
        post=Posts.query.all()
        contacts=Contacts.query.all()
        return render_template('dashboard.html',params=params,post=post,contacts=contacts)

    if request.method=='POST':
        username=request.form.get('uname')
        password=request.form.get('pass')
        if username == params['admin_user'] and password==params['admin_password']:
            session['user']=username
            post=Posts.query.all()
            return render_template('dashboard.html',params=params,post=post)
        else:
            return render_template('login.html',params=params)
    else:
        return render_template('login.html',params=params)


@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if(request.method == 'POST'):
            f= request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
            return redirect('/dashboard')
        else:
            return redirect('/dashboard')



@app.route("/blogpost/<string:post_slug>",methods=['GET'])
def blogpost(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    posts=Posts.query.filter_by().limit(3).all()


    return render_template('blogpost.html',params=params,post=post,posts=posts)

app.run(debug=True)

