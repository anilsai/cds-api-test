FROM python:3.7-buster
RUN apt-get update && apt-get install -y python3 python3-pip
ADD . /home
WORKDIR /home
RUN python3 -m pip install awslambdaric --target /home/
RUN dir
RUN pip3 install .
WORKDIR /home
CMD ["main.lambda_handler.run"]
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric"]