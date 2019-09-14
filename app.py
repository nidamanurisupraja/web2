from flask import Flask,render_template,redirect,url_for,request,flash#modules
import os
from db_setup import Base,Owner,Post
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session
from flask import session as login_session
from functools import wraps  
app=Flask(__name__)
engine=create_engine('sqlite:///mydb.db')
Base.metadata.bind=engine
session=scoped_session(sessionmaker(bind=engine))

def login_required(f):
	@wraps(f)
	def x(*args,**kwargs):
		if 'email' not in login_session:
			return redirect(url_for('login'))
		return f(*args,**kwargs)
	return x


@app.route('/')
@app.route('/home')
def home():
	posts=session.query(Post).all()
	return render_template('home2.html',posts=posts)




@app.route('/register',methods=["POST","GET"])
def register():
	if request.method=="POST":
		name=request.form['name']
		email=request.form['email']
		password=request.form['password']
		owner=Owner(name=name,email=email,password=password)
		session.add(owner)
		session.commit()
		flash("owner successfully created",'success') 
	return render_template('register.html')

@app.route('/newpost',methods=["POST","GET"])
@login_required
def newpost():
	if request.method=="POST":
		title=request.form['title']
		image=request.form['image']
		owner_id=1
		post=Post(title=title,image=image,owner_id=owner_id)
		session.add(post)
		session.commit()
		flash("successfully posted",'success')

	return render_template('newpost.html')

@app.route('/post/<int:post_id>/edit',methods=["POST","GET"])
@login_required
def editpost(post_id):
	if request.method=="POST":
		title=request.form['title']
		image=request.form['image']
		post=session.query(Post).filter_by(id=post_id).one_or_none()
		post.title=title
		post.image=image
		session.add(post)
		session.commit()
		flash("Successfully updated post",'success')
		return redirect(url_for('home'))
	else:
		post=session.query(Post).filter_by(id=post_id).one_or_none()
		return render_template('update.html',post=post)

@app.route('/login',methods=["POST","GET"])
def login():
	if request.method=="POST":
		email=request.form['email']
		password=request.form['password']
		owner=session.query(Owner).filter_by(email=email,password=password).one_or_none()
		if owner==None:
			flash("Invaid Credentials",'danger')
			return redirect(url_for('login'))
		login_session['email']=email
		login_session['name']=owner.name
		flash("Welcome "+str(owner.name),'success')
		return redirect(url_for('home')) 
	return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
	del login_session['email']
	del login_session['name']
	flash('logout successful and visit again','success')
	return redirect(url_for('home'))

@app.route('/post/<int:post_id>/delete')
@login_required
def deletepost(post_id):
	post=session.query(Post).filter_by(id=post_id).one_or_none()
	session.delete(post)
	session.commit()
	flash('post is successfully deleted','danger')
	return redirect("/")

@app.route('/upload')
@login_required
def fileupload():
	return render_template('fileupload.html')

@app.route('/store',methods=["POST","GET"])
@login_required
def store():
	if request.method=="POST":
		file=request.files['file']
		path=os.getcwd()+'/static/images/'
		file.save(path+file.filename)
		return render_template("success.html",name=file.filename)



# always should be last position
if __name__ == '__main__':
	app.secret_key="7730961685"
	app.run(debug=True,port=5000,host="localhost")
