FROM python:3.11
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
WORKDIR /discord_bot
COPY .. app/
ENV PYTHONPATH "${PYTHONPATH}:/app"
CMD ["ls"]
#CMD ["python3", "app/main.py"]
