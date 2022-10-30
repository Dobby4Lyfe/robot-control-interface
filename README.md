# robot-control-interface
node-red system that provides the basic UI and controls for robot

# Getting Started
We expect the following to be available (Linux or WSL2 under Windows 10/11)

## Docker
### **For server type systems, your raspberry pi etc.**
```
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
 ```

### **Windows Desktop or if you want a UI on Linux**
 Install [Docker Desktop](https://www.docker.com/get-started/)

## Docker Compose
```
 sudo apt-get install docker-compose-plugin
```
Now you are ready

You may want to add your current user to the `docker` group, otherwise you will need to `sudo` to control docker

# Running it
From the root of the directory, you can run node-red & mqtt with the following command: 

`docker-compose up -d`

To see what is going on you can read the logs from the containers and follow, if you are having issues:
`docker-compose logs -f` 

# Data

Everything that the two applications create will be stored under `./data/` in this folder.

# Using it

## MQTT
Accessable to other containers on the same docker network as `mqtt://dobby-mqtt-1:1883` or outside of docker on `mqtt://<yourIP>:1883`.

There is no authentication required right now for simplicity since we expect to run on a closed network, but you will need to set your mqtt client name to use the prefix `dobby-` and then provide a useful description for your component so we know what is publishing/subscribing.

## Node-red
In your browser, once it's running you can find it at `http://localhost:1880/` for the flow designer, and `http://localhost:1880/ui` for the dashboard.
