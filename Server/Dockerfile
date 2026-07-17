FROM python:3.13
#create working dir
WORKDIR /usr/local/server

# copy files and install dependancies
COPY --chmod=775 * ./
RUN pip install --no-cache-dir -r requirements.txt 

# expose port for app and create editable server id env variable
EXPOSE 5000
ENV SERVER_ID=0

# create new user to avoid running the app as root
RUN useradd server
USER server

CMD [ "python", "routes.py"]