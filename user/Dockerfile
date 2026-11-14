FROM python:alpine

WORKDIR /app

# copy the required files and directories in the workdir
COPY --parents ./user/./user.py ./user/./databases ./
COPY ./utils/jwt.py  ./requirements.txt ./

# install the Python requirements
RUN pip install -r requirements.txt

# start user.py when the container is started
CMD python ./user.py
