# Imagen base de Python
FROM python:3.10

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todo el contenido del proyecto al contenedor
COPY . .

# Instalar pip actualizado y dependencias del proyecto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exponer el puerto de FastAPI (Railway usará este)
EXPOSE 8000

# Comando para ejecutar la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
