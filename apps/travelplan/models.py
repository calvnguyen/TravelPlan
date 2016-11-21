from __future__ import unicode_literals

from django.db import models
import re
from django.contrib import messages
import bcrypt
from datetime import datetime

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# name cannot contain numbers
NAME_REGEX = re.compile(r'^[^0-9]+$')
# requires a password to have at least 1 uppercase letter and 1 numeric value.
PASS_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*\d).+$')

# Create your models here.

class TripManager(models.Manager):
	def add_trip(self, destination, description, travel_from, travel_to, userId):
		errors = {}
		present = datetime.now()
		errors['destination-error'] = []
		errors['description-error'] = []
		errors['travel-from-error'] = []
		errors['travel-to-error'] = []
		errors['user-error'] = []


		if len(destination) == 0:
			errors['destination-error'].append('Destination\'s Name cannot be empty!')

		if len(description) == 0:
			errors['description-error'].append('Description cannot be empty!')

		if not self.is_date(travel_from):
			errors['travel-from-error'].append("Travel From Cannot be Empty or is not valid!!")

		elif datetime.strptime(travel_from, "%Y-%m-%d") < present:
			errors['travel-from-error'].append('Travel From Date cannot be from the past!')

		if not self.is_date(travel_to):
			errors['travel-to-error'].append("Travel To Cannot be Empty or is not valid!!")

		elif datetime.strptime(travel_to, "%Y-%m-%d") < present:
			errors['travel-to-error'].append('Travel To Date cannot be from the past!')

		if travel_to < travel_from:
			errors['travel-to-error'].append('Travel To Date cannot be before Travel From Date!')


		if len(errors['destination-error']) != 0 or len(errors['description-error']) != 0 or len(errors['travel-from-error']) != 0 or len(errors['travel-to-error']) != 0:
			return (False, errors)

		else:

			users = User.userMgr.filter(id=userId)

			if users:
				user = users[0]
				print "user from trip manager is", user.name
			else:
				errors['user-error'].append('No user exists to associate a trip')
				return (False, errors)

			trips = Trip.tripMgr.filter(destination=destination)
			if trips:
				trip = trips[0]
			else:
				trip = Trip.tripMgr.create(destination=destination, description=description, travel_from=travel_from, travel_to=travel_to, creator=user.name)

			trip.users.add(user)
			return (True, trip)
	
	def is_date(self, traveldate):
		try:
			if traveldate != datetime.strptime(traveldate, "%Y-%m-%d").strftime('%Y-%m-%d'):
				raise ValueError
			return True
   		except ValueError:
			return False

	def add_to_plan(self, userID, tripID):
		errors = {}
		errors['plan-add-error'] = []
		trip = Trip.tripMgr.get(id = tripID)
		users = User.userMgr.filter(id=userID)

		if users:
			user = users[0]
		else:
			errors['plan-add-error'].append('No user exists to add to plan')
			return (False, errors)

		trip.users.add(user)

		return (True, trip)

	def delete(self, itemID):
		errors = {}
		errors['list-delete-error'] = []
		wishes = Wish.wishMgr.filter(id = itemID)
		if wishes:
			wish = wishes[0]
		else:
			errors['list-delete-error'].append('No user exists to delete from list')
			return (False, errors)
		wish.delete()
		return (True, wish)

	def remove_from_list(self, userID, itemID):
		errors = {}
		errors['list-remove-error'] = []
		users = User.userMgr.filter(id=userID)

		if users:
			user = users[0]
		else:
			errors['list-remove-error'].append('No user exists to remove item from list')
			return (False, errors)

		wish = Wish.wishMgr.get(id = itemID)

		wish.users.remove(user)
		return (True, wish)


class UserManager(models.Manager):
	def login(self, username, password):
		errors = {}

		errors['username-error'] = []
		errors['password-error'] = []

		if len(username) < 1:
			errors['username-error'].append("Username cannot be empty!")

		if len(password) < 1:
			errors['password-error'].append("Password cannot be empty!")

		elif len(password) < 8:
			errors['password-error'].append("Password\'s length has to be more than 8 characters!")


		if len(errors['username-error']) != 0 or len(errors['password-error']) != 0:
			return (False, errors)
	
		else:
			try:
				user = User.userMgr.get(username=username)

				if not bcrypt.hashpw(password, user.password.encode('utf-8')) == user.password:
					print "login check - password DO NOT MATCH"
					errors['password-error'].append("Either email/pw is incorrect")	
					return (False, errors)
				elif bcrypt.hashpw(password, user.password.encode('utf-8')) == user.password:
					print "login check - passwords match"
					return (True, user)


			except User.DoesNotExist:
				errors['username-error'].append("Username cannot be found")
				return (False, errors)


	def register(self, name, username, password, passwordconfirm):
		errors = {}
		present = datetime.now()
		errors['name-error'] = []
		errors['username-error'] = []
		errors['password-error'] = []
		errors['password-confirm-error'] = []


		if len(name) < 1:
			errors['name-error'].append("Name cannot be empty!")

		elif len(name) < 3:
			errors['name-error'].append("Name has to be at least 3 characters!")

		elif not NAME_REGEX.match(name):
			errors['name-error'].append("Name cannot contain a number!")

		if len(username) < 1:
			errors['username-error'].append("Username cannot be empty!")

		elif len(username) < 3:
			errors['username-error'].append("Username has to be at least 3 characters!")

		# elif not self.is_date(date_hired):
		# 	errors['date-hire-error'].append("Date hired entered is not valid!!")
		# elif datetime.strptime(date_hired, "%Y-%m-%d") > present:
		# 	errors['date-hire-error'].append("Date hired cannot be from the future!")

		if len(password) < 1:
			errors['password-error'].append("Password cannot be empty!")

		elif len(password) < 8:
			errors['password-error'].append("Password's length has to be more than 8 characters!")

		if len(passwordconfirm) < 1:
			errors['password-confirm-error'].append("Password Confirmation cannot be empty!")
		
		elif len(passwordconfirm) < 8:
			errors['password-confirm-error'].append("Password confirmation's length has to be more than 8 characters!")
		
		if password != passwordconfirm:
			errors['password-confirm-error'].append("Password and password's confirmation must match!")


		if len(errors['password-error']) != 0 or len(errors['password-confirm-error']) != 0 or len(errors['username-error']) != 0 or len(errors['name-error']) != 0:
			return (False, errors)
		
		else:				
			user = User.userMgr.filter(username = username)
			if (user):
				errors['username-error'].append("Username already exists. Please proceed to login or choose another one")
				return (False, errors)
			else:
				hashed = bcrypt.hashpw(password, bcrypt.gensalt().encode('utf-8'))
				user = User.userMgr.create(name=name, username=username, password=hashed)
				user.save()
				return (True, user)


class User(models.Model):
	name = models.CharField(max_length=255)
	username = models.CharField(max_length=255)
	password = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	userMgr = UserManager()


class Trip(models.Model):
	destination = models.CharField(max_length=255)
	description = models.TextField(max_length=500)
	users = models.ManyToManyField(User)
	creator = models.CharField(max_length=255, null=True)
	travel_to = models.CharField(max_length=10, null=True)
	travel_from = models.CharField(max_length=10, null=True)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
	tripMgr = TripManager()