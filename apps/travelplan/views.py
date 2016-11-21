from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from .models import User, Trip
from datetime import datetime


# Create your views here.
def index(request):
  if 'user_id' in request.session:
    return redirect("/listing")
    request.session['status'] = "logged"
  else:
    return redirect("/login") 

def login(request):

  if request.method == "POST": 
    print "im in Login - Post"
    password = request.POST['password'].encode('utf-8')
    result = User.userMgr.login(request.POST['username'], password)

    if result[0]:
      print result[1]
      request.session['user_id'] = result[1].id
      request.session['status'] = "logged"
      return redirect("/listing")
    else:
 
      if 'username-error' in result[1]:
        for msg in result[1]['username-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='username-error')
      if 'password-error' in result[1]:
        for msg in result[1]['password-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='password-error')

    	return redirect("/login")

  elif request.method == "GET":
    	return render(request, 'travelplan/login.html')


def create_user(request):

  if (request.method == "GET"):
    return render(request, "travelplan/index.html")

  elif (request.method == "POST"):
    print "Got Post Info"
    password = request.POST['password'].encode('utf-8')
    result = User.userMgr.register(request.POST['name'], request.POST['username'], password, request.POST['passwordconfirm'])
    print "Got out of register"
    if result[0]:
      print "Able to create ok"
      request.session['user_id'] = result[1].id
      request.session['status'] = "registered"
      return redirect('/listing')
    else:
      print result[1]
      if 'name-error' in result[1]:
        for msg in result[1]['name-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='name-error')
      if 'username-error' in result[1]:
        for msg in result[1]['username-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='login-error')
      if 'password-error' in result[1]:
        for msg in result[1]['password-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='password-error')
      if 'password-confirm-error' in result[1]:
        for msg in result[1]['password-confirm-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='password-confirm-error')

      return redirect('/register')
  else:
    return redirect('/register')

def create_trip(request):
  if (request.method == "GET"):
    return render(request, "travelplan/add.html")
  elif (request.method == "POST"):
    print "Got Post Info"

    result = Trip.tripMgr.add_trip(request.POST['destination'], request.POST['description'], request.POST['travelfrom'], request.POST['travelto'],request.session['user_id'])
    
    if (result[0]):
      # return redirect('/listing')
      print "created trip ok"
      # user = User.userMgr.filter(id=request.session['user_id'])
      # if user:
      #   wishes= Wish.wishMgr.filter(users=user)
      #   print user.query
      #   print wishes.query
      return redirect('/listing')
        
    else:
      if 'destination-error' in result[1]:
        for msg in result[1]['destination-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='destination-error')
      if 'description-error' in result[1]:
        for msg in result[1]['description-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='description-error')
      if 'travel-from-error' in result[1]:
        for msg in result[1]['travel-from-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='travel-from-error')
      if 'travel-to-error' in result[1]:
        for msg in result[1]['travel-to-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='travel-to-error')

      return redirect('/travels/add')
  else:
    return redirect('/login')

def list_plans(request):

  if 'user_id' in request.session:
    print "my user id", request.session['user_id']
    user = User.userMgr.get(id = request.session['user_id'])
   
    print "user id", user.id

    others_trips = Trip.tripMgr.exclude(users__id = user.id)
    print "Everyone's trip items are:"
    for trip in others_trips:
      print trip.destination
    
    user_trips = user.trip_set.all()
    # print user_items.query
    # print "\nuser "  + user.name + " trips are: "
    # for useritem in user_items:
    #   item_users = useritem.users.all()
    #   print "\nitem is:", useritem.item
    #   print "\nthis item is Added by:", item_users[0].name  + "\n"

    context = {'user_trip_listing': user_trips,
              'user_account': user,
              'others_trip_listing': others_trips
              }

    return render(request, 'travelplan/listing.html', context)

  else:
    return redirect("/login")
def show(request, trip_id):

  trip = Trip.tripMgr.get(id = trip_id)

  print "Date format is:", type(trip.travel_from)

  travel_from = datetime.strptime(trip.travel_from, "%Y-%m-%d")
  travel_to = datetime.strptime(trip.travel_to, "%Y-%m-%d")


  trip_users = trip.users.all().exclude(name = trip.creator)

  context = {'users_joining_list': trip_users, 'trip': trip, 'travel_from': travel_from, 'travel_to': travel_to}

  return render(request, 'travelplan/show.html', context)

def add_to_plan(request, trip_id):

  result = Trip.tripMgr.add_to_plan(request.session['user_id'], trip_id)
  if (result[0]):
    return redirect('/listing')
        
  else:
    if 'plan-add-error' in result[1]:
      for msg in result[1]['plan-add-error']:
          messages.add_message(request, messages.ERROR, msg, extra_tags='plan-add-error')
      return redirect('/listing')

def delete_wish(request, wish_id):

  result = Wish.wishMgr.delete(wish_id)

  if (result[0]):
    return redirect('/listing')
  else:
    if 'list-delete-error' in result[1]:
      for msg in result[1]['list-delete-error']:
        messages.add_message(request, messages.ERROR, msg, extra_tags='list-delete-error')
      return redirect('/listing')


def remove_wish(request, wish_id):

  result = Wish.wishMgr.remove_from_list(request.session['user_id'], wish_id)

  if (result[0]):
    return redirect('/listing')

def logout(request):
  request.session.pop('user_id')
  return redirect('/login')