from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import List
from database import get_connection

routerUsuarios = APIRouter(prefix="/usuarios", tags=["Usuarios"])

class Usuario(BaseModel):
    id: int = None
    nombre: str
    email: str

@routerUsuarios.get("/", response_model=List[Usuario])
def obtener_usuarios():
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, email FROM usuarios")
        usuarios = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(usuarios))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")
    finally:
        db.close()

@routerUsuarios.post("/", response_model=Usuario)
def crear_usuario(usuario: Usuario):
    db = get_connection()
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, email) VALUES (%s, %s)", (usuario.nombre, usuario.email))
        db.commit()
        usuario.id = cursor.lastrowid
        return usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")
    finally:
        db.close()

@routerUsuarios.put("/{usuario_id}", response_model=Usuario)
def actualizar_nombre_usuario(usuario_id: int, nombre: str):
    db = get_connection()
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE usuarios SET nombre = %s WHERE id = %s", (nombre, usuario_id))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cursor.execute("SELECT id, nombre, email FROM usuarios WHERE id = %s", (usuario_id,))
        usuario_actualizado = cursor.fetchone()
        return JSONResponse(content=jsonable_encoder(usuario_actualizado))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")
    finally:
        db.close()

@routerUsuarios.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int):
    db = get_connection()
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return {"mensaje": "Usuario eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")
    finally:
        db.close()
