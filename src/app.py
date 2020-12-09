import json

from db import db
import dao
from flask import Flask
from flask import request
from db import Asset, User, Post, Comment, Tag
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
# somehow still uploads images to the bucket even if there is an error
@app.route("/user/image/upload/", methods=["POST"])
def upload_image():
    body = json.loads(request.data)
    image_data = body.get("image_data")
    img_type = body.get("img_type")
    type_id = body.get("type_id")
    # no image data or image type
    if (image_data is None or img_type is None):
        return failure_response("No base64 URL to be found or no image type!")
    # incorrect image type
    if img_type != "profile" and img_type != "recipe":
        return failure_response(img_type)
    asset = Asset(image_data=image_data, img_type=img_type, type_id=type_id)
    db.session.add(asset)
    if img_type == "profile":
        user = User.query.filter_by(id=type_id).first()
        if user is None:
            return failure_response("User cannot be found!")
        user.photo.append(asset)
    elif img_type == "post":
        post = Post.query.filter_by(id=type_id).first()
        if post is None:
            return failure_response("Post cannot be found!")
        post.photos.append(asset)
    db.session.commit()

    return success_response(asset.serialize(), 201)


@app.route("/image/<int:img_id>/")
def get_image(img_id):
    asset = Asset.query.filter_by(id=img_id).first()
    if asset is None:
        return failure_response("Image not found!")
    return success_response(asset.serialize(), 200)

@app.route("/image/<int:img_id>/delete/", methods=["DELETE"])
def delete_image(img_id):
    asset = Asset.query.filter_by(id=img_id).first()
    if asset is None:
        return failure_response("Image not found!")
    salt = asset.salt
    ext = asset.extension
    img_filename = f"{salt}.{ext}"
    asset.delete(img_filename)
    db.session.delete(asset)
    db.session.commit()
    return success_response(asset.serialize())
    

@app.route("/getUsers/")
def getUsers():
    #users = [u.serialize() for u in User.query.all()]
    #return success_response(users, 200)
    return success_response(dao.getUsers())


@app.route("/user/<int:user_id>/")
def getUser(user_id):
    #user = User.query.filter_by(id=user_id).first()
    user = dao.getUser(user_id)
    if user is None:
        return failure_response("User cannot be found!")
    return success_response(user, 200)


@app.route("/register/", methods=["POST"])
def register():

    body = json.loads(request.data)
    username = body.get("username")
    
    password = body.get("password")
    if username is None or password is None:
        return failure_response("No username or password!")

    bio = body.get("bio", "")
    temp_user = dao.getUserByUsername(username=username)
    if temp_user is not None: #if user is not None, then username already exists so no need to check if username-of-temp_user == username 
        if temp_user.get("bio") == bio:
            return failure_response("User already registered!")
        return failure_response("Username already taken!")
    
    user = dao.register(username=username, password=password, bio=bio)
    #user = User(username=username, password=password, bio=bio)
    if user is None:
        return failure_response("The server could not create the user!")
    return success_response(user, 200)

@app.route("/user/<int:follower_user_id>/follow/", methods=["POST"])
def follow(follower_user_id):
    #no error if relationship already exists

    followed_user_id = json.loads(request.data).get("followed_user_id")
    
    if follower_user_id == followed_user_id:
        return failure_response("User and follower ids are the same!")
    if dao.getUser(follower_user_id) is None or dao.getUser(followed_user_id) is None:
        return failure_response("One or both of those users cannot be found!")
    
    follower = dao.follow(follower_user_id=follower_user_id, followed_user_id=followed_user_id)
   
    if follower is None:
        return failure_response("The user was not able to be followed!")

    return success_response(follower)

@app.route("/user/<int:follower_user_id>/unfollow/", methods=["POST"])
def unfollow(follower_user_id):
    #no error if relationship does not exist 

    followed_user_id = json.loads(request.data).get("followed_user_id")

    if follower_user_id == followed_user_id:
        return failure_response("User and follower ids are the same!")
    if dao.getUser(follower_user_id) is None or dao.getUser(followed_user_id) is None:
        return failure_response("One or both of these users cannot be found!")
    
    follower = dao.unfollow(follower_user_id=follower_user_id, followed_user_id=followed_user_id)
    if follower is None:
        return failure_response("The user was not able to be unfollowed!")

    return success_response(follower)

@app.route("/user/<int:user_id>/post/", methods=["POST"])
def post(user_id):

    user = dao.getUser(user_id)
    if user is None:
        return failure_response("User cannot be found!") 

    # case post was not created for whatever reason, possibly because of incorrect request data
    # still need to fix dateTime functionality, time functionality (only accepts ints rn)
    body = json.loads(request.data)
    post = dao.post(
        user_id = user_id,
        title=body.get("title"),
        dateTime=body.get("dateTime"),
        ingredients=body.get("ingredients"),
        recipe=body.get("recipe"),
        recipeTime=body.get("recipeTime"),
        difficultyRating=body.get("difficultyRating"),
        overallRating=body.get("overallRating"),
        priceRating=body.get("priceRating")
    )
    if post is None:
    	return failure_response("Post could not be created!")
    return success_response(post, 200)

# get post by post id
@app.route("/post/<int:post_id>/")
def getPost(post_id):
    post = dao.getPost(post_id)
    if post is None:
        return failure_response("Post does not exist!")
    return success_response(post, 200)5


#don't think we need this, frontend can just call getUser instead 
#@app.route("/user/<int:user_id>/posts/")
# def getPostsByUser(user_id):
#     user = User.query.filter_by(id=user_id).first()
#     if user is None:
#         return failure_response("User does not exist!")
#     return success_response(user.getPosts(), 200)



@app.route("/post/<int:post_id>/delete/", methods=["DELETE"])
def deletePost(post_id):
	post = dao.getPost(post_id)
	if post is None:
		return failure_response("Post was not found!")
	post = dao.deletePost(post_id)
	if post is None:
		return failure_response("The server was not able to delete this post!")
	return success_response(post, 200)




# rate post difficulty (we need a way to make sure than each user can only rate each post once)
# rate post overall (we need a way to make sure than each user can only rate each post once
# add tag to post

# add comment
# delete comment

# get feed -- do this later


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
