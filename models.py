from sqlalchemy import Column, Integer, String
from db import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    nip = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    dmc = Column(String, nullable=False)
    wymiary = Column(String, nullable=False)
    winda = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    kody_startu = Column(String, nullable=False)
    zabudowa = Column(String, nullable=False)
