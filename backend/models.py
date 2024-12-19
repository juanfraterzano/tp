from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Time
from sqlalchemy.orm import relationship
from db import ORMBase, db_instance

class CanchaDb(ORMBase): 
    __tablename__ = 'canchas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(25), nullable=False) 
    techada = Column(Boolean, nullable=False)
    



class ReservaDb(ORMBase):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dia = Column(Date, nullable=False)
    hora = Column(Time, nullable=False) #Hora de inicio del turno
    duracion = Column(Integer, nullable=False) #Duracion en minutos
    telefono_contacto = Column(String(20), nullable=False)
    nombre_contacto = Column(String(100), nullable=False)
    cancha_id = Column(Integer, ForeignKey('canchas.id'), nullable=False)
    cancha = relationship("CanchaDb")


db_instance.create_all()