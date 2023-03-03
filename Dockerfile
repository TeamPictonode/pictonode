# GNU AGPL v3 License
# Written by John Nunley
# Set up ontario-web as a docker container

# Use a node image
FROM node:14

# Add relevant files in the current directory to the container
ADD ./backend /backend
ADD ./frontend /frontend
ADD ./libraries /libraries
ADD ./package.json /package.json
ADD ./package-lock.json /package-lock.json

# Install libcairo, libgirepository1.0-dev, libgegl-dev, and python3-pip
RUN apt-get update && apt-get install -y libcairo2-dev libgirepository1.0-dev libgegl-dev python3-pip python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0

# Install node packages
RUN npm ci

# Set the working directory to /backend/ontario-web
WORKDIR /backend/ontario-web

# Install the required packages
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip install gunicorn

# Run the script that puts together the frontend and backend
RUN python3 ./make_public_dir.py

EXPOSE 8080

# Run the server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "ontario_web:create_app()"]
