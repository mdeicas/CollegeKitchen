from db import User



#create user
#get all users
def getAllUsers():
	return [u.serialize for u in User.query.all()]

#get user
#create post
#get post 
#get all posts

#create comment

