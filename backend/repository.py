from models import CanchaDb, ReservaDb

class NotFoundError(Exception):

    def __init__(self, message):
        super().__init__(message)
        self._status_code = 404

    @property
    def status_code(self):
        return self._status_code
    
class PaddleRepo:
    def getAllCanchas(self, db):
        filas = db.query(CanchaDb).all()
        canchas = []
        for cancha in filas:
            canchas.append({"Id": cancha.id, "Nombre": cancha.nombre, "Techada": cancha.techada})
        if not canchas:
            return "No hay reservas"
        return canchas
    
    def getAllReservas(self, db):
        filas = db.query(ReservaDb).all()
        reservas = []
        for reserva in filas:
            reservas.append({"Id": reserva.id, "Dia": reserva.dia, "Hora": reserva.hora, "Duracion": reserva.duracion, "Telefono contacto": reserva.telefono_contacto, "Nombre contacto": reserva.nombre_contacto, "Cancha": reserva.cancha})
        if not reservas:
            return "No hay reservas"
        return reservas
    
    def getCanchaId(self, id, db):
        cancha = db.get(CanchaDb, id)
        if not cancha:
            raise NotFoundError("Id no encontrada")
        
        return cancha
    
    def getReservaId(self, id, db):
        reserva = db.get(ReservaDb, id)
        if not reserva:
            raise NotFoundError("Id no encontrada")
        
        return reserva
    
    def getReservasDia(self, dia, db):
        reserva = db.query(ReservaDb).filter(ReservaDb.dia == dia).all()
        if not reserva:
            return []
        
        return reserva
    
    def getReservasHora(self, hora, db):
        reserva = db.query(ReservaDb).filter(ReservaDb.hora == hora).all()
        if not reserva:
            return []
        
        return reserva
    
    def getReservasCancha(self, canchaId, db):
        reserva = db.query(ReservaDb).filter(ReservaDb.cancha_id == canchaId).all()
        if not reserva:
            return []
        
        return reserva
    
    def addCancha(self, cancha, db):
        nueva = CanchaDb(nombre=cancha.nombre, techada=cancha.techada)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)

    def addReserva(self, reserva, db):
        nueva = ReservaDb(dia=reserva.dia, hora=reserva.hora, duracion=reserva.duracion, telefono_contacto=reserva.telefono_contacto, nombre_contacto=reserva.nombre_contacto, cancha_id=reserva.cancha_id)
        db.add(nueva)
        db.commit()
        db.refresh(nueva)

    def deleteCancha(self, id, db):
        db.query(ReservaDb).filter(ReservaDb.cancha_id == id).delete()
        borrado = self.getCanchaId(id, db)
        db.delete(borrado)
        db.commit()
        return borrado
    
    def deleteReserva(self, id, db):
        borrado = self.getReservaId(id, db)
        db.delete(borrado)
        db.commit()
        return borrado
    
    def updateCancha(self, id, cancha_actualizada, db):
        cancha_existente = self.getCanchaId(id, db)
        
        cancha_existente.nombre = cancha_actualizada.nombre
        cancha_existente.techada = cancha_actualizada.techada

        db.commit()
        db.refresh(cancha_existente)
        return cancha_existente
    

    def updateReserva(self, id, reserva_actualizada, db):
        reserva_existente = self.getReservaId(id, db)
        
        reserva_existente.dia = reserva_actualizada.dia
        reserva_existente.hora = reserva_actualizada.hora
        reserva_existente.duracion = reserva_actualizada.duracion
        reserva_existente.telefono_contacto = reserva_actualizada.telefono_contacto
        reserva_existente.nombre_contacto = reserva_actualizada.nombre_contacto
        reserva_existente.cancha_id = reserva_actualizada.cancha_id

        db.commit()
        db.refresh(reserva_existente)
        return reserva_existente