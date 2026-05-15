# Usar una imagen base de Python oficial y ligera
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . .

# Hugging Face Spaces requiere que la aplicación escuche en el puerto 7860
EXPOSE 7860

# Comando para ejecutar la aplicación
# Usamos 0.0.0.0 para que sea accesible externamente
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
