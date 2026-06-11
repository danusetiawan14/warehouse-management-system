class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/warehouse_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "warehouse123"