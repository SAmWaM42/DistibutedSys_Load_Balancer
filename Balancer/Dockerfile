FROM python:3.13
#create working dir
WORKDIR /usr/local/balancer

# install docker cli
RUN apt-get update && apt-get install -y docker.io

# install dependancies
COPY --chmod=775 requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt 

# copy remaining files  
COPY --chmod=775 balancer.py ./

# expose port for app 
EXPOSE 5000

CMD [ "python", "balancer.py"]