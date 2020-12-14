import json

from db import db
import dao
from flask import Flask
from flask import request
from db import Asset, User, Post, Comment, Tag
import os

# can probably change the filename
db_filename = "app.db"
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
    imageData = body.get("imageData")
    imgType = body.get("imgType")
    typeId = body.get("typeId")
    # no image data or image type
    if (image_data is None or img_type is None):
        return failure_response("No base64 URL to be found or no image type!")
    # incorrect image type
    if img_type != "profile" and img_type != "recipe":
        return failure_response(img_type)    
    if imgType == "profile":
        user = User.query.filter_by(id=typeId).first()
        if user is None:
            return failure_response("This user does not exist!")
    elif imgType == "post":
        post = Post.query.filter_by(id=typeId).first()
        if post is None:
            return failure_response("This post does not exist!")
    asset = dao.uploadImage(imageData=imageData, imgType=imgType, typeId=typeId)
    if asset is None:
        return failure_response("There was an error creating the asset!")
    return success_response(asset, 201)


@app.route("/image/<int:img_id>/")
def get_image(img_id):
    asset = dao.getImage(img_id)
    if asset is None:
        return failure_response("Image cannot be found!")
    return success_response(asset, 200)

@app.route("/image/<int:img_id>/delete/", methods=["DELETE"])
def delete_image(img_id):
    asset = dao.deleteImage(img_id)
    if asset is None:
        return failure_response("Image not found!")
    return success_response(asset)
    

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

@app.route("/user/<int:user_id>/following/")
def getFollowingUsernames(user_id):
    following = dao.getFollowingUsernames(user_id)
    if following is None:
        return failure_response("User not found!")
    return success_response(following)

@app.route("/user/<int:user_id>/followers/")
def getFollowersUsernames(user_id):
    followers = dao.getFollowersUsernames(user_id)
    if followers is None:
        return failure_response("User not found!")
    return success_response(followers)

@app.route("/user/<int:user_id>/post/", methods=["POST"])
def post(user_id):

    user = dao.getUser(user_id)
    if user is None:
        return failure_response("User cannot be found!") 

    # case post was not created for whatever reason, possibly because of incorrect request data
    # still need to fix dateTime functionality, time functionality (only accepts ints rn)
    body = json.loads(request.data)

    difficultyRating=body.get("difficultyRating")
    if(difficultyRating>3 or difficultyRating<0):
        return failure_response("The difficultyRating must be 1, 2, or 3!")

    priceRating=body.get("priceRating")
    if(priceRating>3 or priceRating<0):
        return failure_response("The priceRating must be 1, 2, or 3!")


    post = dao.post(
        user_id = user_id,
        title=body.get("title"),
        ingredients=body.get("ingredients"),
        recipe=body.get("recipe"),
        recipeTime=body.get("recipeTime"),
        difficultyRating=difficultyRating,
        priceRating=priceRating
    )
    if post is None:
        return failure_response("Post could not be created!")
    return success_response(post, 200)

# add tag to post
@app.route("/post/<int:post_id>/tag/", methods=["POST"])
def addTags(post_id):
    body = json.loads(request.data)
    tags = body.get("tags") # array of strings
    post = dao.getPost(post_id)
    if post is None:
        return failure_response("Post cannot be found!") 
    post = dao.updateTags(post_id, tags=tags)
    if post is None:
        return failure_response("Tags could not be updated!")
    return success_response(post)

# get post by post id
@app.route("/post/<int:post_id>/")
def getPost(post_id):
    post = dao.getPost(post_id)
    if post is None:
        return failure_response("Post does not exist!")
    return success_response(post, 200)

@app.route("/posts/")
def getPosts():
    return success_response(dao.getPosts())

# get posts by user id
@app.route("/user/<int:user_id>/posts/")
def getPostsByUser(user_id):
    posts = dao.getPostsByUser(user_id)
    if posts is None:
        return failure_response("User not found!")
    return success_response(posts, 200)


@app.route("/post/<int:post_id>/delete/", methods=["DELETE"])
def deletePost(post_id):
    post = dao.getPost(post_id)
    if post is None:
        return failure_response("Post was not found!")
    post = dao.deletePost(post_id)
    if post is None:
        return failure_response("The server was not able to delete this post!")
    return success_response(post, 200)

@app.route("/ratings/")
def getAllRatings():
    return success_response(dao.getAllRatings(),200)

@app.route("/post/<int:post_id>/difficulty/")
def getDifficultyRating(post_id):
    post = dao.getPost(post_id)
    if post is None:
        return failure_response("That post was not found!")
    return dao.getDifficultyRating(post_id)

@app.route("/post/<int:post_id>/price/")
def getPriceRating(post_id):
    post = dao.getPost(post_id)
    if post is None:
        return failure_response("That post was not found!")
    return dao.getPriceRating(post_id)

#overall rating routes
@app.route("/post/<int:post_id>/overall/", methods=["POST"])
def rateOverall(post_id):
    body = json.loads(request.data)
    
    score = body.get("score")
    if score < 0 or score > 5:
        return failure_response("The score must be in between 0 and 5!")

    if dao.getPost(post_id) is None:
    	return failure_response("That post was not found!")

    user_id = body.get("user_id")
    if user_id is None or score is None:
        return failure_response("No user_id or score provided!")

    rating = dao.rateOverall(user_id=user_id, post_id=post_id, score=score)
    if rating is None:
        return failure_response("Post was not able to be rated!")
    return success_response(rating, 200)

@app.route("/post/<int:post_id>/overall/")
def getOverallRating(post_id):
    post = dao.getPost(post_id)
    if post is None:
        return failure_response("That post was not found!")
    return dao.getOverallRating(post_id)

#can pass a list of tags, but not neccessary. 
@app.route("/posts/popular/", methods=["POST"])
def getPopularPostsbyTags():
	body = json.loads(request.data)
	tags = body.get("tags") 
	return success_response(dao.getPopularPostsbyTags(tags),200)


@app.route("/user/<int:user_id>/following/posts/", methods=["POST"])
def getFollowingPostsByTags(user_id):
    body = json.loads(request.data)
    tags = body.get("tags") 
    followingPosts = dao.getFollowingPostsByTags(user_id, tags)
    if followingPosts is None:
        return failure_response("User does not exist!")
    return success_response(followingPosts, 200)


#TODO
#1. authentication 


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
