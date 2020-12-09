from db import db, User, Post, Tag, Comment

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
		difficultyRating=kwargs.get("difficultyRating"),
		numDifficultyRatings=1,
		overallRating=kwargs.get("overallRating"),
		numOverallRating=1,
		priceRating=kwargs.get("priceRating"),
		numPriceRating=1
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






































	




