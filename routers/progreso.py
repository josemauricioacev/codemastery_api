from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from database import get_connection
from models import UserProgress

routerProgreso = APIRouter(prefix="/progreso", tags=["Operaciones Progreso"])

# POST: Agregar progreso
@routerProgreso.post("/", response_model=UserProgress)
def agregar_progreso(progreso: UserProgress):
    db = get_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO user_progress (user_id, module_id, completed, completion_date, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """, (
            progreso.user_id,
            progreso.module_id,
            progreso.completed,
            progreso.completion_date
        ))
        db.commit()
        return progreso
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al guardar progreso", "excepcion": str(e)})
    finally:
        db.close()

# PUT: Actualizar progreso
@routerProgreso.put("/", response_model=UserProgress)
def actualizar_progreso(progreso: UserProgress):
    db = get_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            UPDATE user_progress 
            SET completed = %s, completion_date = %s, updated_at = NOW()
            WHERE user_id = %s AND module_id = %s
        """, (
            progreso.completed,
            progreso.completion_date,
            progreso.user_id,
            progreso.module_id
        ))
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="No se encontró el progreso para actualizar.")
        return progreso
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al actualizar progreso", "excepcion": str(e)})
    finally:
        db.close()




# GET: Progreso por módulo
@routerProgreso.get("/curso/{module_id}")
def obtener_por_modulo(module_id: str):
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_progress WHERE module_id = %s", (module_id,))
        datos = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(datos))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al consultar módulo", "excepcion": str(e)})
    finally:
        db.close()

# GET: Todo el progreso
@routerProgreso.get("/")
def obtener_todos_los_progresos():
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT user_id, module_id, completed, completion_date FROM user_progress")
        datos = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(datos))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al obtener todos los progresos", "excepcion": str(e)})
    finally:
        db.close()

# DELETE: Progreso específico
@routerProgreso.delete("/{user_id}/{module_id}")
def eliminar_progreso(user_id: int, module_id: str):
    db = get_connection()
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM user_progress WHERE user_id = %s AND module_id = %s", (user_id, module_id))
        db.commit()
        if cursor.rowcount == 0:
            return JSONResponse(status_code=404, content={"mensaje": "No se encontró el progreso"})
        return {"mensaje": "Progreso eliminado correctamente"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al eliminar progreso", "excepcion": str(e)})
    finally:
        db.close()

# DELETE: Todo el progreso del usuario
@routerProgreso.delete("/usuario/{user_id}")
def eliminar_todo_progreso_de_usuario(user_id: int):
    db = get_connection()
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM user_progress WHERE user_id = %s", (user_id,))
        db.commit()
        return {"mensaje": f"Se eliminó todo el progreso del usuario {user_id}."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al eliminar progreso", "excepcion": str(e)})
    finally:
        db.close()

# GET: Estado completado/incompleto
@routerProgreso.get("/estado/{estado}")
def obtener_por_estado(estado: int):
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_progress WHERE completed = %s", (estado,))
        datos = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(datos))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al filtrar por estado", "excepcion": str(e)})
    finally:
        db.close()

# GET: Progreso por fechas
@routerProgreso.get("/rango-fechas")
def obtener_por_rango_fechas(
    start_date: datetime = Query(..., description="Fecha inicial"),
    end_date: datetime = Query(..., description="Fecha final")
):
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM user_progress 
            WHERE completion_date BETWEEN %s AND %s
        """, (start_date, end_date))
        datos = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(datos))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error en búsqueda por fechas", "excepcion": str(e)})
    finally:
        db.close()

# GET: Usuarios que completaron módulo
@routerProgreso.get("/usuarios/completos/{module_id}")
def usuarios_que_completaron(module_id: str):
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id FROM user_progress 
            WHERE module_id = %s AND completed = 1
        """, (module_id,))
        datos = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(datos))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al obtener usuarios completos", "excepcion": str(e)})
    finally:
        db.close()

# GET: Usuarios que NO completaron módulo
@routerProgreso.get("/usuarios/incompletos/{module_id}")
def usuarios_que_no_completaron(module_id: str):
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id FROM user_progress 
            WHERE module_id = %s AND completed = 0
        """, (module_id,))
        datos = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(datos))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al obtener usuarios incompletos", "excepcion": str(e)})
    finally:
        db.close()

# GET: Resumen del usuario
@routerProgreso.get("/resumen/{user_id}")
def resumen_usuario(user_id: int):
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                SUM(completed = 1) AS completados,
                SUM(completed = 0) AS pendientes
            FROM user_progress
            WHERE user_id = %s
        """, (user_id,))
        resultado = cursor.fetchone()
        return {
            "usuario": user_id,
            "completados": resultado["completados"],
            "pendientes": resultado["pendientes"]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al generar resumen", "excepcion": str(e)})
    finally:
        db.close()



# GET: Todos los usuarios registrados (debe ir antes que /{user_id})
@routerProgreso.get("/usuarios", tags=["Operaciones Usuarios"])
def obtener_usuarios_registrados():
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email FROM users")
        usuarios = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(usuarios))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al obtener usuarios registrados", "excepcion": str(e)})
    finally:
        db.close()

# GET: Progreso individual por ID de usuario
@routerProgreso.get("/{user_id}")
def obtener_progreso_por_usuario(user_id: int):
    db = get_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, module_id, completed, completion_date
            FROM user_progress WHERE user_id = %s
        """, (user_id,))
        datos = cursor.fetchall()
        return JSONResponse(content=jsonable_encoder(datos))
    except Exception as e:
        return JSONResponse(status_code=500, content={"mensaje": "Error al obtener progreso", "excepcion": str(e)})
    finally:
        db.close()


# GET: Obtener todos los usuarios registrados
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

# POST: Crear un nuevo usuario
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

# PUT: Actualizar el nombre de un usuario por ID
@routerUsuarios.put("/{usuario_id}", response_model=Usuario)
def actualizar_nombre_usuario(usuario_id: int = Path(..., title="ID del usuario a actualizar"), nombre: str = Path(..., title="Nuevo nombre del usuario")):
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

# DELETE: Eliminar un usuario por ID
@routerUsuarios.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int = Path(..., title="ID del usuario a eliminar")):
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
