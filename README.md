# Docker Subsance Automation Toolkit

A demo to run a substance automation toolkit's websocket microservice  


## Build  
Assuming docker is already installed,  
### 1. Add installer  
put `Substance_Automation_Toolkit_*-linux-x64-standard.tar.gz` under `/installer`  
### 2. Build with command
```sh
# build the service
docker-compose build sat
```

## Run
```sh
# start sat service in background
docker-compose up sat -d

# run test task client
python client/test.py
```

It will bake a texture-set (ao, normal, position, etc) from highres mesh to lowres mesh,
and feed the result to a sbsar to generate a mask.  