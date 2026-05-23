#Crete a Base image
FROM python:3.11-slim

#Set a Working Directory
#(It will create a folder to save all the file.
#Without it system will become confuse When will it go on to new window
#app become project folder and all files go inside app like app/main.py
WORKDIR / app

#Install System Dependencies
#(Refresh the list of available packages, install compiler, remove unnecessary files and keep the docker compact and slim)
RUN apt-get update && apt-get install -y --no-install-recommends\ build-essential\
    && rm -rf var/lib/apt/lists/*

#Copy Requirements(For Caching Layers)
#(Copies only the dependecy files in container so docker caches this step.Whenever code is changed, it chaches step )
COPY requirements.txt .

#Install Python Dependencies
#-r requirements.txt ----> read packages in this folder and install them
#--no-cache-dir --->
RUN --no-cache-dir -r-requirements.txt

#Copy the whole project
COPY . .

#Expose Fast API Port
#This means this app is supposed to run on port:800
EXPOSE 8000

#Run FastAPI with Uvicorn
CMD ["uvicorn", "fastapi_agent: app", "--host","0.0.0.0", "--port", "8000","--reload"]

#FROM python:3.11-slim
#WORKDIR /app
#RUN apt-get-update && apt-get install --y --no-install-recommends\build-essential\
#    && rm-rf/var/lib/apt/lists/*
#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#COPY . .
#EXPOSE 8000
#CMD ["uvicorn","fastapi_Travel_agent:app","--host","0.0.0.0","--port","8000","--reload"]