# Docker Subsance Automation Toolkit

# Build
## 1. Add installer  
put `Substance_Automation_Toolkit_*-linux-x64-standard.tar.gz` under `/installer`  
## 2. Run
```shell
docker-compose build sat
```

# Test
```shell
docker-compose run test
```

Doc  
https://docs.substance3d.com/sat

docker run -it -v d:/Repo/h-sat/temp:/home docker-sat
sbsbaker run --json preset.json