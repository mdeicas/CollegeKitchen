from db import db, User, Post, Tag, Comment, Rating
from sqlalchemy import func

def getUsers():
	return [u.serialize() for u in User.query.all()]

def getUser(user_id):
	user = User.query.filter_by(id=user_id).first()
	return None if (user is None) else user.serialize()

def getUserByUsername(username):
	user = User.query.filter_by(username=username).first()
	return None if (user is None) else user.serialize()

def register(username, password, bio):
	user = User(username=username, password=password, bio=bio)
	if user is None:
		return None
	db.session.add(user)
	db.session.commit()
	return user.serialize()

def follow(follower_user_id, followed_user_id):
	follower_user = User.query.filter_by(id=follower_user_id).first()
	follower_user.follow(followed_user_id)
	db.session.commit()
	return follower_user.serialize()

def unfollow(follower_user_id, followed_user_id):
	follower_user = User.query.filter_by(id=follower_user_id).first()
	follower_user.unfollow(followed_user_id)
	db.session.commit()
	return follower_user.serialize()

def post(user_id, **kwargs):
	post = Post(
		title=kwargs.get("title"),
		dateTime=kwargs.get("dateTime"),
		ingredients=kwargs.get("ingredients"),
		recipe=kwargs.get("recipe"),
		recipeTime=kwargs.get("recipeTime"),
		#difficultyRating=kwargs.get("difficultyRating"),
		difficultyRating=0,
		#numDifficultyRatings=1,
		#overallRating=kwargs.get("overallRating"),
		overallRating=0,
		#numOverallRating=1,
		#priceRating=kwargs.get("priceRating")#,
		priceRating=0,
		#numPriceRating=1
	)

	user = User.query.filter_by(id=user_id).first()
	user.posts.append(post)

	db.session.add(post)
	db.session.commit()

	return post.serialize()

def getPost(post_id):
	post = Post.query.filter_by(id=post_id).first()
	return None if (post is None) else post.serialize()


def deletePost(post_id):
	post = Post.query.filter_by(id=post_id).first()
	if post is None:
		return None
	db.session.delete(post)
	db.session.commit()
	return post.serialize()


def getAllRatings():
	return [r.serialize() for r in Rating.query.all()]

#difficulty rating methods 
def rateDifficulty(user_id, post_id, score):
	rating = Rating.query.filter_by(post_id=post_id).filter_by(user_id=user_id).first()
	if rating is not None:
		rating.difficultyRating = score
	else:
		post = Post.query.filter_by(id=post_id).first()
		user = User.query.filter_by(id=user_id).first()

		rating = Rating(difficultyRating=score)
		rating.post = post
		rating.user = user
		user.ratings.append(rating)
		db.session.add(rating)
	
	db.session.commit()
	updateDifficultyRating(post_id)
	return rating.serialize()

def getDifficultyRating(post_id):
	return {"difficultyRating": Post.query.filter_by(id=post_id).first().difficultyRating}

def updateDifficultyRating(post_id):
	sumOfRatings = db.session.query(func.sum(Rating.difficultyRating)).filter_by(post_id=post_id).scalar()
	numRatings = db.session.query(func.count(Rating.difficultyRating)).filter_by(post_id=post_id).scalar()
	print(""*3)
	print("the sum of the difficulty ratings is: " + str(sumOfRatings))
	print("the number of difficulty ratings is: " + str(numRatings))
	print(""*3)

	post = Post.query.filter_by(id=post_id).first()
	post.difficultyRating = sumOfRatings/numRatings
	db.session.commit()



#price rating methods 
def ratePrice(user_id, post_id, score):
	rating = Rating.query.filter_by(post_id=post_id).filter_by(user_id=user_id).first()
	if rating is not None:
		rating.priceRating = score
	else:
		post = Post.query.filter_by(id=post_id).first()
		user = User.query.filter_by(id=user_id).first()

		rating = Rating(priceRating=score)
		rating.post = post
		rating.user = user
		user.ratings.append(rating)
		db.session.add(rating)
	
	db.session.commit()
	updatePriceRating(post_id)
	return rating.serialize()

def getPriceRating(post_id):
	return {"priceRating": Post.query.filter_by(id=post_id).first().priceRating}

def updatePriceRating(post_id):
	sumOfRatings = db.session.query(func.sum(Rating.priceRating)).filter_by(post_id=post_id).scalar()
	numRatings = db.session.query(func.count(Rating.priceRating)).filter_by(post_id=post_id).scalar()
	print(""*3)
	print("the sum of the price ratings is: " + str(sumOfRatings))
	print("the number of price ratings is: " + str(numRatings))
	print(""*3)

	post = Post.query.filter_by(id=post_id).first()
	post.priceRating = sumOfRatings/numRatings
	db.session.commit()


#overall rating methods 
def rateOverall(user_id, post_id, score):
	rating = Rating.query.filter_by(post_id=post_id).filter_by(user_id=user_id).first()
	if rating is not None:
		rating.overallRating = score
	else:
		post = Post.query.filter_by(id=post_id).first()
		user = User.query.filter_by(id=user_id).first()

		rating = Rating(overallRating=score)
		rating.post = post
		rating.user = user
		user.ratings.append(rating)
		db.session.add(rating)
	
	db.session.commit()
	updateOverallRating(post_id)
	return rating.serialize()

def getOverallRating(post_id):
	return {"overallRating": Post.query.filter_by(id=post_id).first().overallRating}

def updateOverallRating(post_id):
	sumOfRatings = db.session.query(func.sum(Rating.overallRating)).filter_by(post_id=post_id).scalar()
	numRatings = db.session.query(func.count(Rating.overallRating)).filter_by(post_id=post_id).scalar()
	print(""*3)
	print("the sum of the overall ratings is: " + str(sumOfRatings))
	print("the number of overall ratings is: " + str(numRatings))
	print(""*3)

	post = Post.query.filter_by(id=post_id).first()
	post.overallRating = sumOfRatings/numRatings
	db.session.commit()














































	




