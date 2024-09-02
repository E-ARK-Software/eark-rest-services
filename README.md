# E-ARK REST Services

This repository contains the python source for the E-ARK REST services.

The web client allows a user to upload an information package to the server for validation. The server runs both the eark-validator and commons-ip implementations and returns both results in a tabbed web page.

The services are implemented using the FAST API framework.

## Quick Start

There are a couple of ways of building and running the server locally.

### Checkout project and install dependencies

First clone the project and move into the project directory.

```bash
git clone https://github.com/E-ARK-Software/eark-rest-services.git
cd eark-rest-services
```

Next create a virtual environment (optional but recommended) and install the dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Finally run the `uvicorn` server.

```bash
uvicorn app.main:app --reload
INFO:     Will watch for changes in these directories: ['/home/cfw/Projects/eArchiving/validation/eark-rest-services']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [23442] using WatchFiles
INFO:     Started server process [23444]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The server should now be running and you can access the web client at `http://localhost:8000`. API documenation is available at `http://localhost:8000/docs`.

### Build the Docker image

If you use Docker then you can build and run the server using the provided Dockerfile.

```bash
docker build -t eark-rest-services .

...

# You can map the server to a different port if you wish, e.g. -p 8000:80 == http://localhost:8000
docker run --rm   -p 80:80 --name eark-rest-services eark-rest-services:latest
INFO     Using path /opt/eark-rest/app/main.py                                  
INFO     Resolved absolute path /opt/eark-rest/app/main.py                      
INFO     Searching for package file structure from directories with __init__.py 
         files                                                                  
INFO     Importing from /opt/eark-rest                                          
                                                                                
 ╭─ Python package file structure ─╮                                            
 │                                 │                                            
 │  📁 app                         │                                            
 │  ├── 🐍 __init__.py             │                                            
 │  └── 🐍 main.py                 │                                            
 │                                 │                                            
 ╰─────────────────────────────────╯ 
```

The Docker container exposes port 80 and the docker run command maps this to port 80 on the host machine. You can access the web client at `http://localhost`. API documenation is available at `http://localhost/docs`.
