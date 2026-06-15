# using a lightweight Python image to keep the container small
FROM python:3.11-slim

# set the working directory inside the container
WORKDIR /app

# copy and install dependencies first so Docker can cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the app
COPY . .

# expose the port FastAPI runs on
EXPOSE 8000

# start the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]