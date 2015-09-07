from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

import datetime

Base = declarative_base()

class Role(Base):
	__tablename__ ='role'

	id = Column (Integer, primary_key=True)
	name = Column(String(250))

class Users(Base):
	__tablename__ ='users'

	id = Column(Integer, primary_key=True)
	name = Column(String (250), nullable=False)
	email = Column(String(250))
	picture = Column(String(250))
	no_of_visits = Column(Integer)
	no_of_likes = Column(Integer)
	role_id = Column(Integer, ForeignKey('role.id'))
	role = relationship(Role)
	created_date = Column(DateTime(timezone=True))


class Category(Base):
	__tablename__='category'

	id= Column(Integer, primary_key=True)
	name= Column(String(80))
	no_of_visits = Column(Integer)
	created_date = Column(DateTime(timezone=True))
	user_id = Column(Integer, ForeignKey('users.id'))
	users = relationship(Users)

	@property
	def serialize(self):
		#Returns object in easily serializable format
		return {
			'id' : self.id,
			'name' : self.name,
			'no_of_visits' : self.no_of_visits,
			'created_date' : self.created_date,
			'user_id' : self.user_id,
		}


class Item(Base):
	__tablename__ ='item'

	id= Column(Integer, primary_key=True)
	name = Column(String(80), nullable=False)
	description = Column(String(1000))
	picture_1 = Column(String(300))
	picture_2 = Column(String(300))
	picture_3 = Column(String(300))
	picture_4 = Column(String(300))
	no_of_likes = Column(Integer)
	no_of_visits = Column(Integer)
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	created_date = Column(DateTime(timezone=True))
	user_id = Column(Integer, ForeignKey('users.id'))
	users = relationship(Users)

	@property
	def serialize(self):
		#Returns object in easily serializable format
		return {
			'id' : self.id,
			'name' : self.name,
			'description' : self.description,
			'picture_1' : self.picture_1,
			'picture_2' : self.picture_2,
			'picture_3' : self.picture_3,
			'picture_4' : self.picture_4,
			'no_of_likes' : self.no_of_likes,
			'no_of_visits' : self.no_of_visits,
			'category_id' : self.category_id,
			#'category' : self.category,
			'created_date' : self.created_date,
		}

class Comments_Item(Base):
	__tablename__='comments_item'

	id= Column(Integer, primary_key=True)
	comment = Column(String(400))
	no_of_likes = Column(Integer)
	item_id = Column(Integer, ForeignKey('item.id'))
	item = relationship(Item)
	created_date = Column(DateTime(timezone=True))



engine = create_engine('postgresql:///model')

Base.metadata.create_all(engine)

