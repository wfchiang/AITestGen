FROM python:3.12.2-bullseye as base 

WORKDIR /aitestgen
COPY . . 

FROM base as builder 
RUN pip install -r ./requirements.txt 
RUN pip install . 

FROM builder as final

EXPOSE 8000

CMD ["streamlit", "run", "--server.address", "0.0.0.0", "--server.port", "8000", "--browser.gatherUsageStats", "false", "--server.fileWatcherType", "none", "streamlit_ui/app.py"]