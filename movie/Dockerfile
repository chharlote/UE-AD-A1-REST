FROM python:alpine

WORKDIR /app

# copy the required files and directories in the workdir
COPY --parents ./movie/./movie.py ./movie/./databases ./
COPY ./utils/jwt.py  ./requirements.txt ./

# install the Python requirements
RUN pip install -r requirements.txt

# start movie.py when the container is started
CMD python ./movie.py
