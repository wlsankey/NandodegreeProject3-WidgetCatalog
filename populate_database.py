#IMPORT flask, ORM, and web request modules (Base infrastucture)
#from catalog import app
from flask import Flask, render_template, request, redirect, url_for, flash

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Users, Category, Item, Comments_Item

import httplib2
import json
from flask import make_response
import requests

from datetime import datetime

#IMPORT for JSON API endpoints
from flask import jsonify

#DATABASE SETUP
#Connect to database and create database session

engine = create_engine('postgresql:///model')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

#JSON Categories to populate application for testing

category_json = json.loads("""{
  "all_categories": [
    {
      "created_date": null,
      "id": 29,
      "name": "Books",
      "no_of_visits": 1
    },
    {
      "created_date": null,
      "id": 21,
      "name": "Camping",
      "no_of_visits": 7
    },
    {
      "created_date": null,
      "id": 20,
      "name": "Kitchenware",
      "no_of_visits": 1
    },
    {
      "created_date": null,
      "id": 32,
      "name": "Laptops",
      "no_of_visits": 10
    },
    {
      "created_date": null,
      "id": 27,
      "name": "Music production",
      "no_of_visits": 6
    },
    {
      "created_date": null,
      "id": 35,
      "name": "Philadelphia Foods",
      "no_of_visits": 12
    },
    {
      "created_date": null,
      "id": 31,
      "name": "Susan's Moving Items",
      "no_of_visits": 8
    }
  ]
}""")

# for e in category_json['all_categories']:
#   category_input = Category(name=str(e['name']), id=str(e['id']), no_of_visits=0, user_id=1)
#   session.add(category_input)
#   session.commit()


items_json = json.loads("""
  {
  "all_items": [
    {
      "category_id": 32,
      "created_date": null,
      "description": "Premium construction, excellent portability, fifth-generation Intel Core i5 power\u2014the Dell XPS 13 is as powerful and feature-packed as they get. It also features the world's first infinity display, a virtually borderless 13-inch screen placed into the body of an 11-inch laptop. Compared to the Apple MacBook Air 13, the XPS 13 is 23% smaller with the same size screen.",
      "id": 21,
      "name": "Dell XPS 13 9343-2727SLV Core i5",
      "no_of_likes": null,
      "no_of_visits": null,
      "picture_1": "http://dri1.img.digitalrivercontent.net/Storefront/Company/msintl/images/English/en-INTL-Dell-XPS-13-9343-2727SLV-i5-128GB-Silver-Androidized-CWF-01965/en-INTL-L-Dell-XPS-13-9343-2727SLV-i5-128GB-Silver-Androidized-CWF-01965-mnco.jpg",
      "picture_2": "http://dri1.img.digitalrivercontent.net/Storefront/Company/msintl/images/English/en-INTL-Dell-XPS-13-9343-2727SLV-i5-128GB-Silver-Androidized-CWF-01965/en-INTL-L-Dell-XPS-13-9343-2727SLV-i5-128GB-Silver-Androidized-CWF-01965-RM1-mnco.jpg",
      "picture_3": "",
      "picture_4": ""
    },
    {
      "category_id": 32,
      "created_date": null,
      "description": "Retina Display The 15\u2011inch model has over 5 million pixels so you can retouch your photos or edit a home movie in HD and experience an astounding level of clarity. Text is razor sharp, too, so even everyday things like browsing the web and revising a document are better than ever. It's a display worthy of world's most advanced notebook. Intel Core i7 Fourth-generation Intel Core i7 processors help you power through the most complicated technical computing tasks. Integrated Iris Pro Graphics and advanced NVIDIA graphics give you tons of pixel-driving horsepower. State-of-the-art I/O like Thunderbolt 2 gives you high-performance expansion unprecedented in a notebook. And at the center of it all is an entirely flash-based architecture that makes everything you do incredibly fast and responsive. Specs like these define a whole new standard for notebook computing. Lightweight MacBook Pro packs a lot of power into not a lot of space. Apple designers and engineers reconsidered each detail of ",
      "id": 19,
      "name": "Apple MacBook Pro MGXA2LL/A 15-Inch Laptop",
      "no_of_likes": null,
      "no_of_visits": null,
      "picture_1": "http://ecx.images-amazon.com/images/I/81q3rm8EjhL._SL1500_.jpg",
      "picture_2": "",
      "picture_3": "",
      "picture_4": ""
    },
    {
      "category_id": 31,
      "created_date": null,
      "description": "A nice corner rack for storing wine and wine glasses.",
      "id": 16,
      "name": "Wine Rack",
      "no_of_likes": null,
      "no_of_visits": 3,
      "picture_1": "http://www.cnbhomes.com/wp-content/uploads/2014/10/spacious-metal-corner-wine-rack-FAjQu.jpg",
      "picture_2": "",
      "picture_3": "",
      "picture_4": ""
    },
    {
      "category_id": 35,
      "created_date": null,
      "description": "Dine cheek to cheek at Philadelphia's own little slice of the West Village, Audrey Claire, a Mediterranean BYOB, one of the city's favorites. Between the South-of-France simplicity, Israeli couscous, mezze, grilled fish served head to tail, and the olive oils of those rustic lands, you'll feel like you've taken the grand tour. ",
      "id": 23,
      "name": "Aubrey Claire",
      "no_of_likes": null,
      "no_of_visits": 2,
      "picture_1": "http://www.audreyclaire.com/images/interior_tables.jpg",
      "picture_2": "http://cdn2-b.examiner.com/sites/default/files/styles/image_content_width/hash/9a/00/1338937072_4630_P1010258.JPG?itok=-0Cvv9E1",
      "picture_3": "http://s3-media3.fl.yelpcdn.com/bphoto/7Nt_D_mnCZs2F7wK2EmqzQ/o.jpg",
      "picture_4": "http://s3-media3.fl.yelpcdn.com/bphoto/kzze8Pk3pt75OpestaWkgA/348s.jpg"
    },
    {
      "category_id": 21,
      "created_date": null,
      "description": "A head-mounted flashlight with 18 White LED and 2 Red LED bulbs. Powered by 3 AAA Batteries.",
      "id": 11,
      "name": "LE LED Headlamp",
      "no_of_likes": 0,
      "no_of_visits": 1,
      "picture_1": "http://ecx.images-amazon.com/images/I/61pujMjiEQL._SL1200_.jpg",
      "picture_2": "http://ecx.images-amazon.com/images/I/61anFoqXqZL._SL1200_.jpg",
      "picture_3": "http://ecx.images-amazon.com/images/I/618-l6Zu17L._SL1200_.jpg",
      "picture_4": null
    }
  ]
}
  """)
  


for e in items_json['all_items']:
  item_input = Item(
    name=str(e['name']), 
    id=str(e['id']), no_of_visits=0, 
    category_id=e['category_id'], 
    no_of_likes=0, 
    picture_1=str(e['picture_1']), 
    picture_2=str(e['picture_2']),
    picture_3=str(e['picture_3']), 
    picture_4=str(e['picture_4']),
    user_id=1
    )
  session.add(item_input)
  session.commit()

