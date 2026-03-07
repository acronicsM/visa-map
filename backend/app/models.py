from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String

from .database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    iso_code = Column(String(3), unique=True, index=True, nullable=False)
    visa_type = Column(String(64), nullable=True)
    geometry = Column(Geometry(geometry_type="GEOMETRY", srid=4326), nullable=True)
