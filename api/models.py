from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_picture = db.Column(db.String(200), nullable=False, default='https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationship mapping the employee to related meetings
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')

    # Association proxy to get posts for this user through comments
    posts = association_proxy('comments', 'post',
                                 creator=lambda post_obj: Comment(post=post_obj))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(100), nullable=False, unique=True)
    image = db.Column(db.String(200), default='https://www.hostinger.com/tutorials/wp-content/uploads/sites/2/2021/09/how-to-write-a-blog-post.png')
    category = db.Column(db.String(50), default='uncategorized')
    slug = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationship mapping the post to related comments
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')

    # Association proxy to get users for this post through comments
    users = association_proxy('comments', 'user',
                                  creator=lambda user_obj: Comment(user=user_obj))

    def __repr__(self):
        return f'<Post {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    # Foreign Key to store the post id
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    # Foreign Key to store the user id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    likes = db.Column(db.PickleType, default=[])
    number_of_likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationship mapping the comment to related user
    user = db.relationship('User', back_populates='comments', cascade='all, delete-orphan')

    # Relationship mapping the comment to related post
    post = db.relationship('Post', back_populates='comments', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Comment {self.id}>'
