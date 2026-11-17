FROM python:alpine

WORKDIR /app

# copy the required files and directories in the workdir
COPY --parents ./booking/./booking.py ./booking/./databases ./
COPY ./utils/jwt.py  ./requirements.txt ./

# install the Python requirements
RUN pip install -r requirements.txt

# start booking.py when the container is started
CMD python ./booking.py
