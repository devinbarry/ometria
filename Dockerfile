FROM python:3

ADD ingester.py /
ADD requirements.txt /
RUN pip install -r /requirements.txt
CMD [ "python", "./ingester.py" ]