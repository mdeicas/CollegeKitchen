# CollegeKitchen

CollegeKitchen is an app for college students to share and rate recipes by other students! Users can create their own profiles, follow other users, and explore top rated recipes similar to a social media app. Recipes will have difficulty and price ratings so that students can easily filter for easy and cheap meals. Users can also filter for different tags like "vegan", "mexican" or "dessert" to help with their search. 

Images are stored in an AWS S3 Bucket. 

## Routes
* register a user: "/register/"
* get a specific user: "/user/<int:user_id>/"
* get all users: "/getUsers/"
* follow a user: "/user/<int:follower_user_id>/follow/"
* unfollow a user: "/user/<int:follower_user_id>/unfollow/"
* get following usernames: "/user/<int:user_id>/following/"
* get follower usernames: "/user/<int:user_id>/followers/"
* create a post: "/user/<int:user_id>/post/"
* add a tag: "/post/<int:post_id>/tags/"
* get a post: "/post/<int:post_id>/"
* get all posts: "/posts/"
* delete a post: "/post/<int:post_id>/delete/"
* get a certain user's posts: "/user/<int:user_id>/posts/"
* get posts by filters: "/posts/filter/"
* get popular post with tags: "/posts/popular/"
* get following posts with tags: "/user/<int:user_id>/following/posts/"
* get all ratings: "/ratings/"
* get difficulty rating: "/post/<int:post_id>/difficulty/"
* get price rating: "/post/<int:post_id>/price/"
* give post overall rating: "/post/<int:post_id>/overall/"
* get overall rating: "/post/<int:post_id>/overall/"

## Models used
* Post
* User
* Asset
* Rating
