FROM python:3.8.10

WORKDIR /home/"HelpDeskPython"/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .