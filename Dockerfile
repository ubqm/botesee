FROM python:3.8.10
RUN apt-get update && apt-get install -y python3 && apt-get install -y python3-pip
RUN pip install pipenv
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
COPY . /home/app
WORKDIR /home/app
EXPOSE 5000