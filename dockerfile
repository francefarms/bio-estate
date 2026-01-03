# 1. Use an official Python "engine" as the base
FROM python:3.9-slim

# 2. Set the "Work Folder" inside the container
WORKDIR /app

# 3. Copy your app files from your computer into the container
COPY app.py .
COPY anthracnose.fasta .
COPY pathogen_analyzer.py .

# 4. Install the libraries your app needs to "paint" and "run"
RUN pip install streamlit matplotlib

# 5. Tell the container to "Open a Window" (Port 8501)
EXPOSE 8501

# 6. The command to start your app when the container "wakes up"
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]