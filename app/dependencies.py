from DataCollection.collection import Database

def get_session():
    db = Database()
    try:
        yield db
    except:
        raise