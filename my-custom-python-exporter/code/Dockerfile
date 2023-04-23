FROM python:3.11.1-alpine3.17

# FROM docker-base.artifactory.resource.bank/python:3-alpine
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /root/requirements.txt

# Or any preferred Python version.
LABEL Author="Tomer Aharoni"
LABEL Description="use for sre team in term of monitoring hcp availability"
ADD main.py .
COPY . .
RUN pip install --upgrade pip
RUN pip install -r /root/requirements.txt --trusted-host artifactory.resource.bank
EXPOSE  5000

CMD ["python", "./main.py", "-p 5000"]