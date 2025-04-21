import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'ipl_db.sqlite')}"
    # SQLALCHEMY_DATABASE_URI = 'postgresql://neondb_owner:npg_6gywkml8XSri@ep-holy-wildflower-a54woyks-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "mysecretkey"
