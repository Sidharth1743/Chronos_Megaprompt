"""
Database models for CHRONOS community features
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import timedelta

db = SQLAlchemy()


class User(db.Model):
    """User model for researcher profiles"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    institution = db.Column(db.String(200))
    expertise = db.Column(db.Text)  # JSON array of expertise areas
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    ratings = db.relationship('Rating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    endorsements = db.relationship('Endorsement', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, secret_key, expires_in=86400):
        """Generate JWT token (expires in 24 hours by default)"""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, secret_key, algorithm='HS256')

    @staticmethod
    def verify_auth_token(token, secret_key):
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token

    def get_engagement_stats(self):
        """Get user engagement statistics"""
        return {
            'total_ratings': self.ratings.count(),
            'total_comments': self.comments.count(),
            'total_endorsements': self.endorsements.count(),
            'member_since': self.created_at.strftime('%B %Y')
        }

    def to_dict(self, include_stats=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'institution': self.institution,
            'expertise': self.expertise,
            'bio': self.bio,
            'created_at': self.created_at.isoformat()
        }
        if include_stats:
            data['engagement'] = self.get_engagement_stats()
        return data


class Rating(db.Model):
    """Hypothesis rating/voting model"""
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    hypothesis_id = db.Column(db.String(100), nullable=False, index=True)  # H1, H2, etc.
    unique_id = db.Column(db.String(200), nullable=False, index=True)  # Analysis unique_id
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint: one rating per user per hypothesis
    __table_args__ = (
        db.UniqueConstraint('user_id', 'hypothesis_id', 'unique_id', name='unique_user_hypothesis_rating'),
    )

    def to_dict(self):
        """Convert rating to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'hypothesis_id': self.hypothesis_id,
            'rating': self.rating,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Comment(db.Model):
    """Hypothesis comment/discussion model"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    hypothesis_id = db.Column(db.String(100), nullable=False, index=True)  # H1, H2, etc.
    unique_id = db.Column(db.String(200), nullable=False, index=True)  # Analysis unique_id
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'institution': self.user.institution,
            'hypothesis_id': self.hypothesis_id,
            'comment_text': self.comment_text,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Endorsement(db.Model):
    """Expert endorsement for hypotheses"""
    __tablename__ = 'endorsements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    hypothesis_id = db.Column(db.String(100), nullable=False, index=True)  # H1, H2, etc.
    unique_id = db.Column(db.String(200), nullable=False, index=True)  # Analysis unique_id
    endorsement_text = db.Column(db.Text)  # Optional endorsement statement
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint: one endorsement per user per hypothesis
    __table_args__ = (
        db.UniqueConstraint('user_id', 'hypothesis_id', 'unique_id', name='unique_user_hypothesis_endorsement'),
    )

    def to_dict(self):
        """Convert endorsement to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'full_name': self.user.full_name,
            'institution': self.user.institution,
            'hypothesis_id': self.hypothesis_id,
            'endorsement_text': self.endorsement_text,
            'created_at': self.created_at.isoformat()
        }


def init_db(app):
    """Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
