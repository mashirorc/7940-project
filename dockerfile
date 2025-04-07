FROM python:3.11
WORKDIR /APP
COPY chatbot.py /APP
COPY ChatGPT_HKBU.py /APP
COPY requirements.txt /APP

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "chatbot.py"]