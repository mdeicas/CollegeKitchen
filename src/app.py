import json

from db import db, Post, User
from flask import Flask
from flask import request
from db import Asset
import os

# can probably change the filename
db_filename = "images.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

########## HELPER FUNCTIONS #############
def success_response(data, code=200):
    return json.dumps({"success": True, "data": data}), code


def failure_response(message, code=404):
    return json.dumps({"success": False, "error": message}), code

########## ROUTES ##############

# uploads an image to the bucket
@app.route("/upload_image/", methods=["POST"])
def upload_image():
    body = json.loads(request.data)
    image_data = body.get("image_data")
    if image_data is None:
        return failure_response("No base64 URL to be found!")
    asset = Asset(image_data=image_data)
    db.session.add(asset)
    db.session.commit()
    return success_response(asset.serialize(), 201)

@app.route("/get_image/<int:img_id>")
def get_image(img_id):
    asset = Asset.query.filter_by(id=img_id).first
    if asset is None:
      return failure_response("Image not found!")
    return success_response(asset.serialize(), 200)



@app.route("/getUsers/")
def getUsers():
	users = [u.serialize() for u in User.query.all()]
	return success_response(users, 200)


@app.route("/user/<int:user_id>/")
def get_User(user_id):
	
	#case user does not exist
	return success_response(User.query.filter_by(id=user_id).first().serialize())

@app.route("/register/", methods=["POST"])
def register():
		
	#case user already exists
	#case username is already taken
	#case course is not created for whatever reason, possibly incorrect request data


	body = json.loads(request.data)
	user = User(
		username=body.get("username"),
		password=body.get("password"),
		bio=body.get("bio"),
		)
	db.session.add(user)
	db.session.commit()
	return success_response(user.serialize(), 200)




@app.route("/user/<int:follower_user_id>/follow/", methods=["POST"])
def follow(follower_user_id):
	
	#case either user does not exist
	#case follower id = follower id
	#db handles case where relationship already exists, does not return error message though 

	followed_user_id = json.loads(request.data).get("followed_user_id")

	follower_user = User.query.filter_by(id=follower_user_id).first()
	follower_user.follow(followed_user_id)
	db.session.commit()

	return success_response(follower_user.serialize())


@app.route("/user/<int:follower_user_id>/unfollow/", methods=["POST"])
def unfollow(follower_user_id):

	#case either user does not exist
	#case follower id = follower id
	#db handles case where relationship already exists, does not return error message though 


	followed_user_id = json.loads(request.data).get("followed_user_id")

	follower_user = User.query.filter_by(id=follower_user_id).first()
	follower_user.unfollow(followed_user_id)
	db.session.commit()

	return success_response(follower_user.serialize())

#create post
@app.route("/user/<int:user_id>/post/", methods=["POST"])
def post(user_id):
	
	#case user does not exist
	#case post was not creeated for whatever reason, possibly because of incorrect request data

	#still need to fix dateTime functionality, time functionality (only accepts ints rn)

	body = json.loads(request.data)
	post = Post(
		title=body.get("title"),
		dateTime=body.get("dateTime"),
		ingredients=body.get("ingredients"),
		recipe=body.get("recipe"),
		recipeTime=body.get("recipeTime"),
		difficultyRating=body.get("difficultyRating"),
		numDifficultyRatings=1,
		overallRating=body.get("overallRating"),
		numOverallRating=1, 
		priceRating=body.get("priceRating"),
		numPriceRating=1
		)

	user = User.query.filter_by(id=user_id).first()
	user.posts.append(post)

	db.session.add(post)
	db.session.commit()
	
	return success_response(post.serialize(), 200)

#get post by post id
#get posts by user id
#delete post
#rate post difficulty (we need a way to make sure than each user can only rate each post once)
#rate post overall (we need a way to make sure than each user can only rate each post once
#add tag to post

#add comment
#delete comment

#get feed -- do this later 



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)