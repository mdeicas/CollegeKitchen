from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET = "recipeappimages"
S3_BASE_URL = f"https://{S3_BUCKET}.s3-us-east-2.amazonaws.com"

# an image or asset
class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    img_type = db.Column(db.String, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("Posts.id"), nullable=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=True)
    base_url = db.Column(db.String, nullable=True)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)

    def __init__(self, **kwargs):
        self.img_type = kwargs.get("img_type")
        if self.img_type == "profile":
            self.profile_id = kwargs.get("type_id")
        elif self.img_type == "post":
            self.post_id = kwargs.get("type_id")

        self.create(kwargs.get("image_data")) # create image

    def serialize(self):
        if self.img_type == "post":
            type_id = self.post_id
        elif self.img_type == "profile":
            type_id = self.profile_id
        return {
            "image_id": self.id,
            "img_type": self.img_type,
            "type_id": type_id,
            "url": f"{self.base_url}/{self.salt}.{self.extension}"
        }

    def create(self, image_data):
        try:
            # given a base64 string --> .png --> png
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f"Extension {ext} not supported!")

            # secure way of generating random string for image name
            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
            )

            # remove header of base64 string and open image
            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            

            img_filename = f"{salt}.{ext}"
            self.upload(img, img_filename)

        except Exception as e:
            print(f"Unable to create image due to {e}")

    def upload(self, img, img_filename):
        try:
            # save image temporariliy on server
            img_temploc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temploc)

            # upload image to S3
            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temploc, S3_BUCKET, img_filename)

            # make S3 image url public
            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET, img_filename)
            object_acl.put(ACL="public-read")

            os.remove(img_temploc)

        except Exception as e:
            print(f"Unable to upload image due to {e}")


# must be here, before User model
followers = db.Table("Followers",
    db.Column("followerID", db.Integer, db.ForeignKey("Users.id")),
    db.Column("followedID", db.Integer, db.ForeignKey("Users.id"))
    )


class User(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    bio = db.Column(db.String)

    posts = db.relationship("Post", cascade="delete")
    comments = db.relationship("Comment", cascade="delete")
    photo = db.relationship("Asset", cascade="delete")
    followed = db.relationship(  # users that are followed by this user
        "User",
        secondary=followers, # links LHS(this user) with its entries in followers table
        primaryjoin=(followers.c.followerID == id), # links RHS (users this user follows) with their entries in the followers table
        secondaryjoin=(followers.c.followedID == id), # "followers" is the RHS version of followed
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic")


    def follow(self, followed_user_id):
        followed_user = User.query.filter_by(id=followed_user_id).first()
        if not self.is_following(followed_user):
            self.followed.append(followed_user)

    def unfollow(self, followed_user_id):
        followed_user = User.query.filter_by(id=followed_user_id).first()
        if self.is_following(followed_user):
            self.followed.remove(followed_user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followedID == user.id).count() > 0

    def getUser(self, user_id):
        return User.query.filter_by(id=user_id).first()

    def getFollowersUsernames(self):
        return [self.getUser(u.followerID).username for u in db.session.query(followers).filter(followers.c.followedID==self.id).all()]

    def serialize(self):
        return {
            "user_id": self.id,
            "username": self.username,
            "bio": self.bio,
            "posts": [p.serialize() for p in self.posts],
            "is_following": [u.username for u in self.followed],
            "followed_by": self.getFollowersUsernames()
            #"followed_by": [u.username for u in db.session.query(followers).filter(followers.c.followedID==self.id).all()]
        }


class Post(db.Model):
    __tablename__ = "Posts"
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String, nullable=False)
    dateTime = db.Column(db.Integer, nullable=False) # need to change to datetime later
    ingredients = db.Column(db.String, nullable=False)
    recipe = db.Column(db.String)
    recipeTime = db.Column(db.Integer, nullable=False)

    # 1..3 corresponds to easy medium hard
    difficultyRating = db.Column(db.Integer, nullable=False)
    numDifficultyRatings = db.Column(db.Integer, nullable=False)
    # integer 1..5 (5 stars)
    overallRating = db.Column(db.Integer, nullable=False)
    numOverallRating = db.Column(db.Integer, nullable=False)
    # integer 1.. 3/4/5 (dollar signs)
    priceRating = db.Column(db.Integer, nullable=False)
    numPriceRating = db.Column(db.Integer, nullable=False)


    userID = db.Column(db.Integer, db.ForeignKey("Users.id"))

    comments = db.relationship("Comment", cascade="delete")
    tags = db.relationship("Tag", cascade="delete")
    photos = db.relationship("Asset", cascade="delete")

    def rateDifficulty(self, rating):
        self.difficultyRating = ((self.difficultyRating * self.numDifficultyRatings) + rating)/(self.numDifficultyRatings + 1)
        self.numDifficultyRatings = self.numDifficultyRatings + 1
    def rateOverall(self, rating):
        self.overallRating = ((self.overallRating * self.numOverallRating) + rating)/(self.numOverallRating + 1)
        self.numOverallRating = self.numOverallRating + 1
    def ratePrice(self, rating):
        self.priceRating = ((self.priceRating * self.numPriceRating) + rating)/(self.numPriceRating + 1)
        self.numPriceRating = self.numPriceRating + 1

    def serialize(self):
        return {
            "post_id": self.id, 
            "title": self.title, 
            "dateTime": self.dateTime, 
            "ingredients": self.ingredients, 
            "recipe": self.recipe, 
            "recipeTime": self.recipeTime, 
            
            "difficultyRating": self.difficultyRating,
            "overallRating": self.overallRating, 
            "priceRating": self.priceRating, 

            "user_id": self.userID,
            "comments": [c.serialize(view="post") for c in self.comments],
            "tags": [t.serialize(view="post") for t in self.tags],

            "photos": [p.serialize for p in self.photos]
        }

class Comment(db.Model):
    __tablename__ = "Comments"
    id = db.Column(db.Integer, primary_key=True)

    comment = db.Column(db.Integer, nullable=False)

    userID = db.Column(db.Integer, db.ForeignKey("Users.id"))
    postID = db.Column(db.Integer, db.ForeignKey("Posts.id"))

    def serialize(self):
        return {
        "comment_id": self.id, 
        "comment": self.comment, 
        "user_id": self.userID, 
        "post_id": self.postID
        }

class Tag(db.Model):
    __tablename__ = "Tags"
    id = db.Column(db.Integer, primary_key=True)

    tag = db.Column(db.Integer, nullable=False)

    postID = db.Column(db.Integer, db.ForeignKey("Posts.id"))

    def serialize(self):
        return {
        "tag_id": self.id, 
        "tag": self.tag, 
        "post_id": self.postID
        }
