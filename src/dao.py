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

def getFollowingUsernames(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    return [u.username for u in user.followed]

def getFollowersUsernames(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    return user.getFollowersUsernames()

def getFollowingPosts(user_id):
    following = getFollowingUsernames(user_id)
    if following is None:
        return None
    allPosts = []
    for f in following:
        followed = User.query.filter_by(username=f).first()
        posts = getPostsByUser(followed.id)
        allPosts.append(posts)
    return allPosts

def uploadImage(imageData, imgType, typeId):
    asset = Asset(image_data=imageData, img_type=imgType, type_id=typeId)
    if asset is None:
        return None
    db.session.add(asset)
    if imgType == "profile":
        user = User.query.filter_by(id=typeId).first()
        user.photo.append(asset)
    elif imgType == "post":
        post = Post.query.filter_by(id=typeId).first()
        post.photos.append(asset)
    db.session.commit()
    return asset.serialize()

def getImage(img_id):
    asset = Asset.query.filter_by(id=img_id).first()
    if asset is None:
        return None
    return asset.serialize()

def deleteImage(img_id):
    asset = asset = Asset.query.filter_by(id=img_id).first()
    if asset is None:
        return None
    salt = asset.salt
    ext = asset.extension
    img_filename = f"{salt}.{ext}"
    asset.delete(img_filename)
    db.session.delete(asset)
    db.session.commit()
    return asset.serialize()

def post(user_id, **kwargs):
	post = Post(
		title=kwargs.get("title"),
		dateTime=kwargs.get("dateTime"),
		ingredients=kwargs.get("ingredients"),
		recipe=kwargs.get("recipe"),
		recipeTime=kwargs.get("recipeTime"),
		difficultyRating=kwargs.get("difficultyRating"),
		overallRating=0,
		priceRating=kwargs.get("priceRating")
	)

	user = User.query.filter_by(id=user_id).first()
	user.posts.append(post)

	db.session.add(post)
	db.session.commit()

	return post.serialize()


def getPost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    return None if (post is None) else post.serialize()

def getPosts():
    return [p.serialize() for p in Post.query.all()]

def getPostsByUser(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return None
    return user.getPosts()


def deletePost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return None
    db.session.delete(post)
    db.session.commit()
    return post.serialize()

def getAllRatings():
    return [r.serialize() for r in Rating.query.all()]

def getDifficultyRating(post_id):
    return {"difficultyRating": Post.query.filter_by(id=post_id).first().difficultyRating}

def addTag(post_id, tags):
    post = getPost(post_id)
    post.setTag(tags)


def getPriceRating(post_id):
	return {"priceRating": Post.query.filter_by(id=post_id).first().priceRating}


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





