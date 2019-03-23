from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///perfumes.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Delete PerfumeCompanyName if exisitng.
session.query(PerfumeCompanyName).delete()
# Delete PerfumeName if exisitng.
session.query(PerfumeName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
FirstUser1 = User(name="Srinivas Reddy",
             email="nivas0803@gmail.com",
             picture='')
session.add(FirstUser1)
session.commit()
print ("Successfully Add First User")
# Create sample perfumes models
Model1 = PerfumeCompanyName(name="FOGG",
                        user_id=1)
session.add(Model1)
session.commit()

Model10 = PerfumeCompanyName(name="AXE",
                        user_id=1)
session.add(Model10)
session.commit()

Model11 = PerfumeCompanyName(name="ENGAGE",
                        user_id=1)
session.add(Model11)
session.commit()

Model12 = PerfumeCompanyName(name="MELODY",
                        user_id=1)
session.add(Model12)
session.commit()

Model3 = PerfumeCompanyName(name="YARDLEY",
                        user_id=1)
session.add(Model3)
session.commit()

# Perfume details
Perfume1 = PerfumeName(name="Nepolian",
                       flavour="Blue Forest",
                       color="Blue",
                       cost="160rs",
                       rlink="https://bit.ly/2TX0ESY",
                       date=datetime.datetime.now(),
                       perfumecompanynameid=1,
                       user_id=1)
session.add(Perfume1)
session.commit()

Perfume2 = PerfumeName(name="AXE POVOKE DEO",
                       flavour="Chocolate",
                       color="Red",
                       cost="220rs",
                       rlink="https://bit.ly/2HstiWp",
                       date=datetime.datetime.now(),
                       perfumecompanynameid=2,
                       user_id=1)
session.add(Perfume2)
session.commit()

Perfume3 = PerfumeName(name="ENGAGE URGE",
                       flavour="Urge",
                       color="Black",
                       cost="190rs",
                       rlink="https://bit.ly/2Y9XA55",
                       date=datetime.datetime.now(),
                       perfumecompanynameid=3,
                       user_id=1)
session.add(Perfume3)
session.commit()

Perfume4 = PerfumeName(name="MELODY ORCHESTRA",
                       flavour="Orchestra",
                       color="SkyBlue",
                       cost="550rs",
                       rlink="https://bit.ly/2uh6O1T",
                       date=datetime.datetime.now(),
                       perfumecompanynameid=4,
                       user_id=1)
session.add(Perfume4)
session.commit()

Perfume5 = PerfumeName(name="YARDLEY LONDON",
                       flavour="Breeza",
                       color="Green",
                       cost="1099rs",
                       rlink="https://bit.ly/2ucuzYW",
                       date=datetime.datetime.now(),
                       perfumecompanynameid=5,
                       user_id=1)
session.add(Perfume5)
session.commit()

Perfume6 = PerfumeName(name="MELODY ORCHESTRA",
                       flavour="Orchestra",
                       color="SkyBlue",
                       cost="550rs",
                       rlink="https://bit.ly/2uh6O1T",
                       date=datetime.datetime.now(),
                       perfumecompanynameid=6,
                       user_id=1)
session.add(Perfume6)
session.commit()

print("Your Sample database has been inserted!")
