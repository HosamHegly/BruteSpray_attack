FROM python
WORKDIR /code
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN playwright install && playwright install-deps
EXPOSE 5000
COPY . . 
RUN pwd
ENTRYPOINT ["python", "main.py"]