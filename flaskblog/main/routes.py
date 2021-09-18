from flask import render_template, request, Blueprint, flash, redirect, url_for,session
from flaskblog.models import Record, Databio,Dataflow, Post, Comment, Brandname, Catagoryname, SellerId, User, Product ,CustomerOrder
from flaskblog.main.forms import Contact, Brand, Catagory, Sellerform,Addproducts,Upproducts
from flaskblog import db, bcrypt
from flask import request,make_response
import requests
from flaskblog.users.utils import get_country ,call_api
from flask_login import current_user, login_required
from flaskblog.users.utils import save_pro_picture
import secrets
import json
import pdfkit
import stripe
import datetime

main = Blueprint('main', __name__)

@main.route("/")
def indexmain():

	return render_template('indexmain.html')


@main.route("/app")
def index():

	return render_template('index.html')

@main.route("/community")
def home():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', posts=posts ,title='Community')


@main.route("/about")
def about():
	form = Contact()
	if form.validate_on_submit():
		flash('Your post has been created!', 'success')
		return redirect(url_for('main.index'))

	return render_template('about.html', title='About' , form=form)

@main.route("/weather")
def weather():
	if request.headers.getlist("X-Forwarded-For"):
		ip = request.headers.getlist("X-Forwarded-For")[0]
	else:
		ip = request.remote_addr
	country = get_country(ip)
	weather=call_api(country[3],country[4])
	return render_template('weather.html', title='weather' ,country=country,weather=weather)

@main.route("/addlocation", methods=['GET', 'POST'])
@login_required
def brands():
	if current_user.is_authenticated:
		if current_user.username == "admin01":
			form = Brand()
			if form.validate_on_submit():
				bran = Brandname(brand_name=form.name.data, brand_det=form.shortdis.data)
				db.session.add(bran)
				db.session.commit()
				flash('Your post has been created!', 'success')
				return redirect(url_for('main.index'))
			return render_template('brand.html', title='Add Brand' , form=form)
	return "<h3>Admin Login Required.</h3>"

@main.route("/addtype", methods=['GET', 'POST'])
@login_required
def catagories():
	if current_user.is_authenticated:
		if current_user.username == "admin01" or current_user.username == "admin02" or current_user.username == "admin03":
			form = Catagory()
			if form.validate_on_submit():
				cata = Catagoryname(catagory_name=form.name.data, catagory_det=form.shortdis.data)
				db.session.add(cata)
				db.session.commit()
				flash('Your post has been created!', 'success')
				return redirect(url_for('main.index'))
			return render_template('catagory.html', title='Add Catagory' , form=form)
	return "<h3>Admin Login Required.</h3>"

@main.route("/admin/registration", methods=['GET', 'POST'])
def sellerreg():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	else:
		form = Sellerform()
		if form.validate_on_submit():
			hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
			user = User(username=form.username.data, email=form.email.data, password=hashed_password,birth_date=form.birth_date.data,type='sell')
			sellid=SellerId(username=form.username.data, email=form.email.data, birth_date=form.birth_date.data,password=form.password.data,nid=form.nid.data,phone=form.phone.data,address=form.address.data)
			db.session.add(sellid)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('main.index'))
	return render_template('seller.html', title='Seller registration',form=form)

@main.route('/admin/add_user', methods=['GET','POST'])
@login_required
def adddproduct():
	if current_user.is_authenticated:
		if current_user.type == 'sell':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			form = Addproducts()
			if form.validate_on_submit():
				name = form.name.data
				#price = form.price.data
				#discount = form.discount.data
				#stock = form.stock.data
				#colors = form.colors.data
				desc = form.discription.data
				brand = request.form.get('brand')
				category = request.form.get('category')
				image_1 = save_pro_picture(form.image_1.data)
				image_2 = save_pro_picture(form.image_2.data)
				image_3 = save_pro_picture(form.image_3.data)
				product = Product(name=name,price=price,discount=discount,stock=stock,colors=colors,desc=desc,category=category,brand=brand,image_1=image_1,image_2=image_2,image_3=image_3,author5=current_user)
				db.session.add(product)
				#print(product)
				flash('Your product has been added!', 'success')
				#flash(f'The product {name} was added in database','success')
				db.session.commit()
				return redirect(url_for('main.index'))
			else:
				print(form.errors.items())
	else:
		return "<h3>Seller Shop Login Required.</h3>"
	return render_template('product.html', form=form, title='Add a Product', brands=brands,categories=categories)



@main.route('/seller/product', methods=['GET','POST'])
@login_required
def seller_product():
	brands = Brandname.query.all()
	categories = Catagoryname.query.all()
	if current_user.is_authenticated:
		if current_user.type == 'sell':
			brands = Brandname.query.all()
			categories = Catagoryname.query.all()
			product = Product.query.filter_by(author5=current_user)
		else:
			return "<h3>Seller Shop Login Required.</h3>"

	else:
		return "<h3>Seller Shop Login Required.</h3>"

	return render_template('selleradmin.html', title='Products', brands=brands,categories=categories,products=product)




@main.route('/thanks')
def thanks():
    return render_template('thank.html')





@main.route('/send_data/biometric/<tag>/<data>',methods=['GET'])
def sendbio(tag, data):
	iot = User.query.filter_by(username=tag).first_or_404()
	final = Databio.query.order_by(Databio.id.desc()).first()
	print(final)
	useges = Dataflow.query.filter(Dataflow.date_posted > final.date_posted).all()
	water = 0
	for i in useges:
		water = water + float(i.data)*10
	row = Record(prof=final.data, date_posted=final.date_posted, data=water)
	db.session.add(row)
	db.session.commit()
	send_data = Databio(tag=tag,data=data)
	db.session.add(send_data)
	db.session.commit()

	return '<h1>Thank you</h1>'

@main.route('/send_data/flow/<tag>/<data>',methods=['GET'])
def sendflow(tag, data):
	iot = User.query.filter_by(username=tag).first_or_404()
	send_data = Dataflow(tag=tag,data=data)
	db.session.add(send_data)
	db.session.commit()

	return '<h1>Thank you</h1>'

@main.route('/dashboard',methods=['GET','POST'])
def dashboard():
	rec = Record.query.all()
	now = datetime.date.today()
	noow = datetime.datetime.now()
	my_time = datetime.datetime.min.time()
	now = datetime.datetime.combine(now, my_time)
	tuse = 0
	oneuse = 0
	twouse = 0
	threeuse = 0
	fouruse = 0
	onehuse = 0
	twohuse = 0
	threehuse = 0
	fourhuse = 0
	for i in rec:
		if i.date_posted >= now:
			tuse = tuse + float(i.data)

			if i.prof == '1':
				oneuse = oneuse + float(i.data)

			if i.prof == '2':
				twouse = twouse + float(i.data)

			if i.prof == '3':
				threeuse = threeuse + float(i.data)

			if i.prof == '4':
				fouruse = fouruse + float(i.data)

	his = [
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
		]
	rmv = datetime.timedelta(1)
	prev = now - rmv
	for j in range(7):
		for i in rec:
			if i.date_posted >= prev and i.date_posted <= now:
				if i.prof == '1':
					onehuse = onehuse + float(i.data)

				if i.prof == '2':
					twohuse = twohuse + float(i.data)

				if i.prof == '3':
					threehuse = threehuse + float(i.data)

				if i.prof == '4':
					fourhuse = fouruse + float(i.data)
		his[j][0] = onehuse
		his[j][1] = twohuse
		his[j][2] = threehuse
		his[j][3] = fourhuse
		onehuse = 0
		twohuse = 0
		threehuse = 0
		fourhuse = 0
		now = now - rmv
		prev = prev -rmv


	useruse=[oneuse , twouse ,threeuse , fouruse]
	peruse = [(oneuse/220)*100 , (twouse/220)*100 , (threeuse/220)*100 , (fouruse/220)*100]
	ledv = {
			1: oneuse,
			2: twouse,
			3: threeuse,
			4: fouruse
			}
	sorted_values = sorted(ledv.values())
	sorted_dict = {}

	for i in sorted_values:
	    for k in ledv.keys():
	        if ledv[k] == i:
	            sorted_dict[k] = ledv[k]
	            break
	profserial = sorted_dict.keys()
	dataserial = sorted_dict.values()
	print(sorted_dict)
	return render_template('dashboard.html' , now=noow, rec = rec, con = tuse, useruse = useruse , per = peruse, his=his, ledpro = profserial , leddata = dataserial)


@main.route('/profile',methods=['GET','POST'])
def profile():
	rec = Record.query.all()
	now = datetime.date.today()
	my_time = datetime.datetime.min.time()
	now = datetime.datetime.combine(now, my_time)
	tuse = 0
	oneuse = 0
	twouse = 0
	threeuse = 0
	fouruse = 0
	onehuse = 0
	twohuse = 0
	threehuse = 0
	fourhuse = 0
	for i in rec:
		if i.date_posted >= now:
			tuse = tuse + float(i.data)

			if i.prof == '1':
				oneuse = oneuse + float(i.data)

			if i.prof == '2':
				twouse = twouse + float(i.data)

			if i.prof == '3':
				threeuse = threeuse + float(i.data)

			if i.prof == '4':
				fouruse = fouruse + float(i.data)

	his = [
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
		]
	rmv = datetime.timedelta(1)
	prev = now - rmv
	for j in range(7):
		for i in rec:
			if i.date_posted >= prev and i.date_posted <= now:
				if i.prof == '1':
					onehuse = onehuse + float(i.data)

				if i.prof == '2':
					twohuse = twohuse + float(i.data)

				if i.prof == '3':
					threehuse = threehuse + float(i.data)

				if i.prof == '4':
					fourhuse = fouruse + float(i.data)
		his[j][0] = onehuse
		his[j][1] = twohuse
		his[j][2] = threehuse
		his[j][3] = fourhuse
		onehuse = 0
		twohuse = 0
		threehuse = 0
		fourhuse = 0
		now = now - rmv
		prev = prev -rmv


	useruse=[oneuse , twouse ,threeuse , fouruse]
	peruse = [(oneuse/220)*100 , (twouse/220)*100 , (threeuse/220)*100 , (fouruse/220)*100]
	ledv = {
			1: oneuse,
			2: twouse,
			3: threeuse,
			4: fouruse
			}
	sorted_values = sorted(ledv.values())
	sorted_dict = {}

	for i in sorted_values:
	    for k in ledv.keys():
	        if ledv[k] == i:
	            sorted_dict[k] = ledv[k]
	            break
	profserial = sorted_dict.keys()
	dataserial = sorted_dict.values()
	print(sorted_dict)
	return render_template('profile.html' , rec = rec, con = tuse, useruse = useruse , per = peruse, his=his, ledpro = profserial , leddata = dataserial)





@main.route('/authority',methods=['GET','POST'])
def authority():
	rec = Record.query.all()
	now = datetime.date.today()
	my_time = datetime.datetime.min.time()
	now = datetime.datetime.combine(now, my_time)
	tuse = 0
	oneuse = 0
	twouse = 0
	threeuse = 0
	fouruse = 0
	onehuse = 0
	twohuse = 0
	threehuse = 0
	fourhuse = 0
	for i in rec:
		if i.date_posted >= now:
			tuse = tuse + float(i.data)

			if i.prof == '1':
				oneuse = oneuse + float(i.data)

			if i.prof == '2':
				twouse = twouse + float(i.data)

			if i.prof == '3':
				threeuse = threeuse + float(i.data)

			if i.prof == '4':
				fouruse = fouruse + float(i.data)

	his = [
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
			[0,0,0,0],
		]
	rmv = datetime.timedelta(1)
	prev = now - rmv
	for j in range(7):
		for i in rec:
			if i.date_posted >= prev and i.date_posted <= now:
				if i.prof == '1':
					onehuse = onehuse + float(i.data)

				if i.prof == '2':
					twohuse = twohuse + float(i.data)

				if i.prof == '3':
					threehuse = threehuse + float(i.data)

				if i.prof == '4':
					fourhuse = fouruse + float(i.data)
		his[j][0] = onehuse
		his[j][1] = twohuse
		his[j][2] = threehuse
		his[j][3] = fourhuse
		onehuse = 0
		twohuse = 0
		threehuse = 0
		fourhuse = 0
		now = now - rmv
		prev = prev -rmv


	useruse=[oneuse , twouse ,threeuse , fouruse]
	peruse = [(oneuse/220)*100 , (twouse/220)*100 , (threeuse/220)*100 , (fouruse/220)*100]
	ledv = {
			1: oneuse,
			2: twouse,
			3: threeuse,
			4: fouruse
			}
	sorted_values = sorted(ledv.values())
	sorted_dict = {}

	for i in sorted_values:
	    for k in ledv.keys():
	        if ledv[k] == i:
	            sorted_dict[k] = ledv[k]
	            break
	profserial = sorted_dict.keys()
	dataserial = sorted_dict.values()
	print(sorted_dict)
	return render_template('authority.html' , rec = rec, con = tuse, useruse = useruse , per = peruse, his=his, ledpro = profserial , leddata = dataserial)