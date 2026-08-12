from auth_database import Base,engine
import auth_models

Base.metadata.drop_all(bind=engine)   #to update , delete first , then update
Base.metadata.create_all(bind=engine)

#copy pasted from create_table.py