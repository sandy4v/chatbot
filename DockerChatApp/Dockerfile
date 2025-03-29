FROM python:3.11
EXPOSE 8502
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . ./
ENTRYPOINT [ "streamlit", "run", "main.py", "--server.port=8502", "--server.address=0.0.0.0" ]