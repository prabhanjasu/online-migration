FROM python:3
RUN apt-get -y update && apt-get install -y python

# working directory
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt


# copy all files to the container
COPY . /code/

# Install pip requirements
#RUN python3 -m pip install --no-cache-dir -r requirements.txt

CMD psql postgres 
CMD python3 main.py