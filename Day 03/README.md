# Day 3: Docker Flags, Deep Dive into Dockerfile, and Exposing Containers | CKA Certification Course 2025

## Video reference for Day 3 is the following:

[![Watch the video](https://img.youtube.com/vi/MQ8fYqZwiQs/maxresdefault.jpg)](https://youtu.be/MQ8fYqZwiQs)

---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

### **Important Docker Flags**

![Docker Flags Overview](/images/3a.png)

### **Additional Info**

# **Nginx** is not just a webserver, it is also used as a load balancer, caching server and also as a Kubernetes Ingress Controller (More about this in upcoming lectures).

```bash
docker run nginx
```

Docker daemon will look for the nginx image locally. If not found then it downloads the image from docker hub. As we execute docker run, docker daemon will download nginx and run as a container in foreground mode.

Container will be up and running. Since the container is ran in foreground, we cannot see the status of running containers in the same terminal. To view the status, open a new terminal and execute **docker ps**. 

If we execute **CTRL + C** and exit, then the container will go to exited status. Container will get exited as it has done the job for which it was started. This container was started to run a webserver. By default nginx webserver will run on port 80. Webserver was running but we have terminated that using **CTRL + C**. 

If we want to have the container run in background (detached mode) then use docker flag (-d) **docker run -d nginx** along with port mapping and a custom name for the image as mentioned below.

------

```bash
docker run -d -p 8080:80 --name my-nginx-cont nginx
```

This command performs several key actions:
1. **Detached Mode (`-d`)**:  
   Runs the container in the background, freeing up your terminal for other tasks.  
2. **Port Mapping (`-p 8080:80`)**:  
   Maps port **80** in the container (default Nginx port) to port **8080** on your host machine.  
3. **Container Name (`--name my-nginx-cont`)**:  
   Assigns the container the name `my-nginx-cont` for easier identification and management.

Once this command is executed, you can access the Nginx default page by opening `http://localhost:8080` in your browser.

### **Additional Info**

If someone is coming from outside, the first thing they will connect to is the host machine (in this case on Port 8080). After host machine they will connect to container (in this case nginx default Port 80).

Once the request reaches my host machine on port 8080, it gets redirected to the default nginx webserver running on port 80. **Now Port 8080 on my host machine is reserved for this container running nginx.** 

**We need to use a different port# while port mapping, if we want to run nginx on another container.** Example below:

```bash
docker run -d -p 8081:80 --name my-nginx-cont-01 nginx
```

The default nginx port number remains the same but the port number used by the host machine will change.

Before proceeding further, go to app.py and understand the application code.

------

### **Dockerfile Instructions and Their Purposes**

1. **`FROM`**:  
   Defines the **base image** to build your application.  
   Example: `FROM ubuntu:latest`

2. **`ADD`**:  
   Copies files/directories from the host to the container and automatically extracts archives (e.g., `.tar.gz`).  
   Example: `ADD app.tar.gz /app`

3. **`RUN`**:  
   Executes commands during the image build process (e.g., installing software, configuring files).  
   Example: `RUN apt-get update && apt-get install -y nginx`

4. **`COPY`**:  
   Similar to `ADD` but **only copies files/directories** (no extraction or URL handling).  
   Example: `COPY app.py /app/app.py`

5. **`EXPOSE`**:  
   Documents the port on which the container’s application will listen. Note: It doesn’t actually open the port; you need to use the `-p` flag when running the container.  
   Example: `EXPOSE 5000`

6. **`CMD`**:  
   Specifies the **default command** to run when the container starts. This can be overridden with `docker run <image-name> <command>`.  
   Example: `CMD ["python", "app.py"]`

7. **`ENTRYPOINT`**:  
   Defines the command that will always execute when the container starts. You can append arguments via `docker run <image-name> <arguments>`. To completely override this, use the `--entrypoint` flag.  
   Example: `ENTRYPOINT ["nginx", "-g", "daemon off;"]`

---

### **Example Dockerfile**

Below is an example `Dockerfile` that builds a lightweight Python Flask application:

```dockerfile
# Use a lightweight Python image as the base. Slim images does not contain the documentation and troubleshooting tooling like ping, DNS etc., which is why the are smaller in size.
# Smaller images are less prone to vulnerabilities as their attack surface is less.  
FROM python:3.9-slim  

# Set the working directory inside the container. WORKDIR creates the directory in this case /app if it doesn't exist and sets it as the default working directory.
# If multiple WORKDIR instructions are used, each one is relative to the previous one unless an absolute path is specified.
WORKDIR /app  

# Copy the application file from the host to the container
ADD app.py /app/app.py  

# Install the necessary Python library
RUN pip install flask  

# Expose the port where the app will listen
EXPOSE 5000  

# Specify the default command to run the application
CMD ["python", "app.py"] # exec form
# CMD python app.py # shell form (execute either shell or exec form while building the image. exec form is recommended)

```

**Now that we have created the Docker file and the application code is also available, go ahead and build the docker Image.**

```bash
docker build -t my-python-image .
```

**Once the image is built then tag the image before pushing the image to docker hub.**

```bash
docker tag my-python-image dinesh2758/my-python-image:v1
```

To view the new image which is tagged and pushed, use **docker images** command.

**Now that the image is tagged, go ahead and push the image to docker hub registry.**

```bash
docker push dinesh2758/my-python-image:v1
```

**Create a container using this image. Port mapping should be done carefully. As we already used 8080 & 8081 on our Host machine, we use 8082 while creating this container. Application listens on Port 5000**

```bash
docker run -d -p 8082:5000 --name my-python-cont dinesh2758/my-python-image:v1
```

Use **docker ps** to view the status of the running container. Access the site i.e., localhost:8082 in a web browser.

---

<img width="961" height="417" alt="image" src="https://github.com/user-attachments/assets/6cd0990b-0b39-425d-be4a-48b919427e95" />

To view the processes running on newly created container, there will only be one single process running i.e., python app.py. As the application was ran in exec form, we are only seeing one process. Refer Dockerfile in README.md to know the format of Shell form. It is better to avoid shell form whereever possible as it will add an additional process which cannot receives signals directly and can cause problems.

```bash
docker top my-python-cont
```

### **Shell Form vs Exec Form in `CMD`**

| **Feature**              | **Shell Form**                                      | **Exec Form**                                      |
|--------------------------|-----------------------------------------------------|----------------------------------------------------|
| **Syntax**               | `CMD <command>`                                     | `CMD ["executable", "param1", "param2"]`           |
| **Execution**            | Runs the command through the shell (`/bin/sh -c`).  | Runs the command directly without a shell.         |
| **Environment Variables**| Supports shell expansion and environment variables. | Does not support shell expansion (e.g., `$VAR`).    |
| **PID 1 Signal Handling**| The shell process becomes PID 1, so it can’t receive signals directly. | The specified executable becomes PID 1 and handles signals directly. |
| **Complex Commands**     | Supports more complex commands, like chaining commands with `&&` & `double pipe`. | Best suited for simple commands with no shell features. |
| **Common Use Case**      | When you need shell features, like piping or chaining commands. | When you want the command to run directly and efficiently. |
| **Examples**             | `CMD echo "Hello World"`                           | `CMD ["echo", "Hello World"]`                      |

---

**To login to the docker container running our Python Application, use below command. Also, it will land into /app WORKDIR as it is specified to be the default directory**

```bash
docker exec -it my-python-cont bash
```

### **Conclusion**

Understanding these Docker flags, Dockerfile instructions, and their nuances is critical for anyone working with containers. From running detached containers with port mappings to defining clear image build instructions in Dockerfiles, these concepts lay the foundation for effective containerized application development. Mastering the differences between `CMD` forms and leveraging Docker’s powerful commands will greatly enhance your ability to create scalable, efficient, and reliable containerized systems.  

Remember, Docker simplifies the development, testing, and deployment process by providing consistency and portability across environments. As you dive deeper, these core concepts will serve as building blocks for more advanced workflows, including multi-container orchestration and CI/CD pipelines. 🚀

---
