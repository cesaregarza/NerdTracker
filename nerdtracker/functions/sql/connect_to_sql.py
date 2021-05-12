import sqlalchemy as db
from ...constants.sensitive_data import db_data

def return_engine():
    db_url = f"{db_data['username']}:{db_data['password']}@{db_data['db_url']}"
    engine = db.create_engine(f"mysql+pymysql://{db_url}")
    return engine