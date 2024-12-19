from repository import PaddleRepo, NotFoundError
from models import ReservaDb
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db import db_instance
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, time, timedelta, datetime

import logging
logging.basicConfig()
# Activar logs detallados para el motor
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

# Activar logs para el manejo de transacciones
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)

# Activar logs para el manejo de ORM (si lo usas)
logging.getLogger('sqlalchemy.orm').setLevel(logging.DEBUG)
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.DEBUG
)


app = FastAPI()
repositorio = PaddleRepo()
#para conexion con el front
origins = [ "http://localhost:3000" ]
app.add_middleware(CORSMiddleware,
    allow_origins=origins,  # Orígenes permitidos
    allow_credentials=True,  # Permite enviar cookies o credenciales
    allow_methods=["*"],  # Métodos permitidos (GET, POST, etc.)
    allow_headers=["*"],  # Headers permitidos)
)

class Cancha(BaseModel):
    nombre: str
    techada: bool

class CanchaUpdate(BaseModel):
    nombre: str
    techada: bool

class Reserva(BaseModel):
    dia: date
    hora: time
    duracion: int
    telefono_contacto: str
    nombre_contacto: str
    cancha_id: int

class ReservaUpdate(BaseModel):
    dia: date
    hora: time #Hora de inicio
    duracion: int #Duracion en minutos
    telefono_contacto: str
    nombre_contacto: str
    cancha_id: int

@app.get("/")
def getRoot():
    return "Proyecto final"

@app.get("/canchas")
def getAllCanchas(db: Session = Depends(db_instance.get_db)):
    return repositorio.getAllCanchas(db)

@app.get("/reservas")
def getAllReservas(db: Session = Depends(db_instance.get_db)):
    return repositorio.getAllReservas(db)

@app.get("/canchas/id/{id}")
def getCanchaId(id:int, db: Session = Depends(db_instance.get_db)):
    try:
        return repositorio.getCanchaId(id, db)
    except NotFoundError as e:
        raise HTTPException(e.status_code, "Id no encontrado")
    
@app.get("/reservas/id/{id}")
def getReservaId(id:int, db: Session = Depends(db_instance.get_db)):
    try:
        return repositorio.getReservaId(id, db)
    except NotFoundError as e:
        raise HTTPException(e.status_code, "Id no encontrado")
    
@app.get("/reservas/dia/{dia}")
def getReservaDia(dia:date, db: Session = Depends(db_instance.get_db)):
    reservas = repositorio.getReservasDia(dia, db)
    if not reservas:
        return {"Mensaje":"No hay reservas en ese dia"}
    return reservas
    
@app.get("/reservas/hora/{hora}")
def getReservaHora(hora:time, db: Session = Depends(db_instance.get_db)):
    reservas = repositorio.getReservasHora(hora, db)
    if not reservas:
        return {"Mensaje":"No hay reservas para esa hora"}
    return reservas
    
@app.get("/reservas/cancha/{canchaId}")
def getReservasCancha(canchaId: int, db: Session = Depends(db_instance.get_db)):
    reservas = repositorio.getReservasCancha(canchaId, db)
    if not reservas:
        return {"Mensaje":"No hay reservas para esa cancha"}
    return reservas
    
@app.post("/cancha")
def agregarCancha(cancha:Cancha, db: Session = Depends(db_instance.get_db)):
    nueva = Cancha(nombre=cancha.nombre, techada=cancha.techada)
    repositorio.addCancha(nueva, db)
    return {"mensaje": "Cancha agregada con éxito", "Nueva Cancha": nueva}

@app.post("/reserva")
def agregarReserva(reserva:Reserva, db: Session = Depends(db_instance.get_db)):
    try:
        verificarReserva(-1, reserva, db)
    except HTTPException as e:
        logging.error(f"Error al crear la reserva: {e}")
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    nueva = Reserva(dia=reserva.dia, hora=reserva.hora, duracion=reserva.duracion, telefono_contacto=reserva.telefono_contacto, nombre_contacto=reserva.nombre_contacto, cancha_id=reserva.cancha_id)
    repositorio.addReserva(nueva, db)
    return {"mensaje": "Reserva agregada con éxito", "Nueva Reserva": nueva}


@app.delete("/cancha/{id}")
def borrarCancha(id: int, db: Session = Depends(db_instance.get_db)):
    try:
        borrada = repositorio.deleteCancha(id, db)
        return {"mensaje": "Auto borrado exitosamente", "Cancha borrada": borrada}
    except NotFoundError as e:
        raise HTTPException(e.status_code, "Id de la cancha no encontrada")
    
@app.delete("/reserva/{id}")
def borrarReserva(id: int, db: Session = Depends(db_instance.get_db)):
    try:
        borrada = repositorio.deleteReserva(id, db)
        return {"mensaje": "Reserva borrado exitosamente", "Reserva borrada": borrada}
    except NotFoundError as e:
        raise HTTPException(e.status_code, "Id de la reserva no encontrada")
    
@app.put("/cancha/{id}")
def updateCancha(id: int, cancha: CanchaUpdate, db: Session = Depends(db_instance.get_db)):
    try:
        actualizada = repositorio.updateCancha(id, cancha, db)
        return {"mensaje": "Cancha actualizada exitosamente", "cancha": actualizada}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/reserva/{id}")
def updateReserva(id: int, reserva: ReservaUpdate, db: Session = Depends(db_instance.get_db)):
    try:
        verificarReserva(id, reserva, db)
        actualizada = repositorio.updateReserva(id, reserva, db)
        return {"mensaje": "Reserva actualizada exitosamente", "reserva": actualizada}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    except HTTPException as e:
        logging.error(f"Error al crear la reserva: {e}")
        raise HTTPException(status_code=e.status_code, detail=str(e))


def verificarReserva(id: int, reservaNueva: Reserva, db:Session = Depends(db_instance.get_db)):
    if reservaNueva.dia < date.today(): 
        raise HTTPException(status_code=409, detal="No se puede reservar un día pasado")
    if ((reservaNueva.hora > time(22, 0)) or (reservaNueva.hora < time(8, 0))): 
        raise HTTPException(status_code=409, detail="Las canchas estan cerradas despues de las 22pm hasta 8am")
    if ((reservaNueva.duracion) > 120 or (reservaNueva.duracion < 30)):
        raise HTTPException(status_code=409, detail="Las reservas tienen una duracion maxima de 120 minutos y una duracion minima de 30 minutos")
    if not reservaNueva.telefono_contacto.isdigit():
        raise HTTPException(status_code=409, detail="El numero de contacto solo puede contener digitos")
    
    reservaNuevaInicio = datetime.combine(reservaNueva.dia, reservaNueva.hora)
    if reservaNueva.dia == date.today() and reservaNuevaInicio < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No se puede reservar una hora pasada")

    cancha = repositorio.getCanchaId(reservaNueva.cancha_id, db)
    if not cancha:
        raise HTTPException(status_code=409, detail="La cancha especificada no existe")

    reservas = repositorio.getReservasCancha(reservaNueva.cancha_id, db)
    if not reservas:
        return
    
    reservaNuevaFin = reservaNuevaInicio + timedelta(minutes=reservaNueva.duracion)
    #Recupero la reserva de la DB para acceder al id y verificar si son la misma reserva, para poder solaparlas
    #mismaReserva = db.query(ReservaDb).filter(ReservaDb.id == id).first()
    #if mismaReserva:
    #    return
    for reservaExistente in reservas:
        reservaExistenteInicio = datetime.combine(reservaExistente.dia, reservaExistente.hora)
        reservaExistenteFin = reservaExistenteInicio + timedelta(minutes=reservaExistente.duracion)     
        if reservaNueva.dia == reservaExistente.dia:
            if (reservaExistenteInicio < reservaNuevaFin) and (reservaNuevaInicio < reservaExistenteFin) and (id!=-1 or reservaExistente.id != id) :
                raise HTTPException(status_code=409, detail="La cancha ya esta ocupada en ese horario")