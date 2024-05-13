from sqlalchemy import create_engine

engine = create_engine('sqlite:///robko240.db')
engine.connect()

