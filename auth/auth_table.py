from auth_database import Base,engine
import auth_models

Base.metadata.create_all(bind=engine)

#copy pasted from create_table.py