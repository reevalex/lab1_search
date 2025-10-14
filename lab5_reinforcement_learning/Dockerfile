FROM python:3.8-slim

WORKDIR /app
COPY . /app

# Install pinned dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install jupyter

EXPOSE 8888
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--NotebookApp.token=''"]
