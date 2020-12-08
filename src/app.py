import json

from db import db
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
    users = [u.serialize() for u in User.query.all()]
    return success_response(users, 200)


@app.route("/user/<int:user_id>/")
def get_User(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User cannot be found!")
    return success_response(user.serialize(), 200)


@app.route("/register/", methods=["POST"])
def register():

    body = json.loads(request.data)
    username = body.get("username")
    password = body.get("password")
    bio = body.get("bio", "")
    temp_user = User.query.filter_by(username=username).first()
    if username is None or password is None:
        return failure_response("No username or password!")
    if temp_user.username == username: # cases user already registered or name taken
        if temp_user.password == password and temp_user.bio == bio:
            return failure_response("User already registered!")
        return failure_response("Username already taken!")
    user = User(username=username, password=password, bio=bio)
    db.session.add(user)
    db.session.commit()
    return success_response(user.serialize(), 200)


@app.route("/user/<int:follower_user_id>/follow/", methods=["POST"])
def follow(follower_user_id):

    user = User.query.filter_by(id=follower_user_id).first()
    followed_user_id = json.loads(request.data).get("followed_user_id")
    followed_user = User.query.filter_by(id=followed_user_id).first()
    # case either user does not exist
    if user is None or followed_user is None:
        return failure_response("User cannot be found!")
    # case follower id = follower id
    if follower_user_id == followed_user_id:
        return failure_response("User and follower ids are the same!")
    # db handles case where relationship already exists, does not return error message though

    follower_user = User.query.filter_by(id=follower_user_id).first()
    follower_user.follow(followed_user_id)
    db.session.commit()

    return success_response(follower_user.serialize())


@app.route("/user/<int:follower_user_id>/unfollow/", methods=["POST"])
def unfollow(follower_user_id):

    user = User.query.filter_by(id=follower_user_id).first()
    followed_user_id = json.loads(request.data).get("followed_user_id")
    followed_user = User.query.filter_by(id=followed_user_id).first()
    # case either user does not exist
    if user is None or followed_user is None:
        return failure_response("User cannot be found!")
    # case follower id = follower id
    if follower_user_id == followed_user_id:
        return failure_response("User and follower ids are the same!")
    # db handles case where relationship already exists, does not return error message though

    follower_user = User.query.filter_by(id=follower_user_id).first()
    follower_user.unfollow(followed_user_id)
    db.session.commit()

    return success_response(follower_user.serialize())

# create post
@app.route("/user/<int:user_id>/post/", methods=["POST"])
def post(user_id):

    # case user does not exist
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User cannot be found!")
    # case post was not creeated for whatever reason, possibly because of incorrect request data
    # still need to fix dateTime functionality, time functionality (only accepts ints rn)

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

# get post by post id
@app.route("/post/<int:post_id>/")
def getPost(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post does not exist!")
    return success_response(post.serialize(), 200)


# get posts by user id
@app.route("/user/<int:user_id>/posts/")
def getPostsByUser(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User does not exist!")
    return success_response(user.getPosts(), 200)

# delete post
# rate post difficulty (we need a way to make sure than each user can only rate each post once)
# rate post overall (we need a way to make sure than each user can only rate each post once
# add tag to post

# add comment
# delete comment

# get feed -- do this later


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
