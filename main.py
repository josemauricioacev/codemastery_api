from fastapi import FastAPI
from routers import progreso
from routers import usuarios

app = FastAPI(
    title='Api Codemastery', 
    description='Api de Codemastery para el curso de FastAPI',
    version='1.0.1'
)
app.include_router(progreso.routerProgreso)
app.include_router(usuarios.routerUsuarios)

@app.get('/', tags=['Inicio'])
def main():
    return {'hello FastAPI':'Codemastery'}

@app.get("/pingdb")
def pingdb():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        return {"status": "ok", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
