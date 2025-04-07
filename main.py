from fastapi import FastAPI
from routers import progreso

app = FastAPI(
    title='Api Codemastery', 
    description='Api de Codemastery para el curso de FastAPI',
    version='1.0.1'
)
app.include_router(progreso.routerProgreso)


@app.get('/', tags=['Inicio'])
def main():
    return {'hello FastAPI':'Codemastery'}


