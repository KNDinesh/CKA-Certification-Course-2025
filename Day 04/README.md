# Day 4: Docker Flags, Deep Dive into Dockerfile, and Exposing Containers | CKA Certification Course 2025

## Video reference for Day 4 is the following:

[![Watch the video](https://img.youtube.com/vi/34l1gRszQS4/maxresdefault.jpg)](https://youtu.be/34l1gRszQS4)

---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---


## **Specifying a Custom Dockerfile Name and Understanding the Build Command in Docker**

When working with Docker, the default name for a Dockerfile is **`Dockerfile`**. However, you can specify a custom name to suit different purposes (e.g., development vs. production environments). This flexibility allows better organization of your project while leveraging Docker's powerful build capabilities.

---

## **Why Use a Custom Name for Dockerfile?**

In certain cases, having multiple Dockerfiles is essential:
- **Environment-Specific Builds**: Use custom names like `Dockerfile.dev` for development and `Dockerfile.prod` for production.
- **Complex Projects**: When different services in your project need distinct Dockerfiles, custom names help keep everything structured.
- **Clarity**: Clearly named Dockerfiles make it easier for teams to understand the purpose of each file.

---

## **Building an Image with a Custom Dockerfile Name**

To build an image using a custom-named Dockerfile, use the `-f` flag in the `docker build` command.

### **Command Syntax**
```bash
docker build -t <image-name> -f <path-to-custom-dockerfile> <build-context>
```

Create basic docker file with any name and build the image. If we do not specify `-f` flag, while building the image, it will throw **failed to read dockerfile: no such file or directory error**. However as soon as we update the file with **FROM** (instruction) as the first word, VS Code understood that it could be a dockerfile and changes the icon.

### **Explanation of Flags**
- **`-t <image-name>`**: Assigns a name (or tag) to the built image.
- **`-f <path-to-custom-dockerfile>`**: Specifies the custom Dockerfile to use.
- **`<build-context>`**: The directory containing files required for the build. This includes the Dockerfile (if not specified with `-f`) and any other files referenced during the build.

=> As we saw in previous Dockerfile examples, we will use a (.) at the end of docker build command which itself is build context. 

=> Anything which is required for building the image (in Python application example **python app.py** in last session) is the build context. 

=> It is always recommended to only keep the necessary files and folders in build context while building the image. 

=> Having README.md or any other file which is not related to application should not be maintained in build context. 

=> Because docker copies everything that is present in the build context to the docker daemon.

---

## **Understanding the Build Context**

The **build context** is the directory Docker uses to locate files for the build process. All files inside this directory are sent to the Docker daemon, allowing Dockerfile instructions like `COPY` and `ADD` to access them.

### **Key Points About the Build Context**
- **Accessibility**: Files outside the build context cannot be accessed during the build.
- **Optimization**: Use a `.dockerignore` file to exclude unnecessary files from the build context, reducing the size of the transfer to the Docker daemon.

### **Example: Building with a Custom Build Context**
If the custom Dockerfile and build context are located in different directories:
```bash
docker build -t entry-image -f /path/to/custom-dockerfile /path/to/build-context
```
- The `-f` flag points to the Dockerfile's location.
- The build context is specified as `/path/to/build-context`.

Once the build is complete and image gets created, execute docker run command with docker image which got created using custom Dockerfile name. Use cmd file for practice.

```bash
docker images
docker run <docker-image-with-custom-Dockerfile-name>
```

Once container successfully ping google.com four times, it will go into exited state.

If we execute **docker run <docker-image-with-custom-Dockerfile-name> ls** it will run the ls command in the container and the output will be printed in the terminal.

We can also override this instead of google.com, we will ping amazon.com

```bash
docker run <docker-image-with-custom-Dockerfile-name> ping -c 4 amazon.com
```

CMD instruction can be completely overriden by the command we supply. It cannot only be ping, we can execute any command to override it as we saw using ls command above.

---

Use entrypoint file now and build the image. Repeat same process like build the image and run the image similar to cmd. This container will also ping google.com and gets exited. 

The major difference with CMD and ENTRYPOINT is that, using CMD we can **override** the executables over the command line docker run where as with ENTRYPOINT, we can **Append** another command in the executable. However if we use ping again to get appended then it will not work. 

To do this in practice, create a new Dockerfile with some name and update the content below
```Dockerfile
FROM ubuntu:latest
ENTRYPOINT ["echo", "This is ENTRYPOINT"]
```

Then build the image and run the container from that image. This will print "This is ENTRYPOINT" in the terminal.

Now, if we want to append something, we can simple run the docker container again and this time while executing **docker run <image-name> "Append"** This will print the output as This is ENTRYPOINT Append in the terminal.

When to use the CMD and when to use ENTRYPOINT?

CMD and ENTRYPOINT may seem similar but they serve distinct purposes. The key difference is that, the ENTRYPOINT is used to specify the primary executable for the container essentially telling docker that the container is designed to run a specific application like we saw in the ping and echo examples. If you try to override it with another command or executable, it might not behave as expected or might fail like we saw in ping example. On the otherhand, CMD provides default arguments or a command that can be overriden if desired. 

**Use CMD when you want to provide a default command that can be fully overriden. Use ENTRYPOINT, when you want a default command that appends arguments passed during docker run.**

If we are designing an application that just pings something, then the ideal way to design that application is using both CMD and ENTRYPOINT in the same file. Refer **ec** for more details.

**When you use the --entrypoint flag in the docker run command, it effectively overrides the ENTRYPOINT and CMD instructions specified within the Dockerfile. The CMD instruction becomes irrelevant as it's designed to provide arguments for the original ENTRYPOINT, which is no longer in effect.**

Ex:

```bash
docker run --entrypoint ls ec-image -l
```

**The **-l** flag provided after **ls** is an argument specifically for the ls command. It instructs **ls** to display a long listing of files. One thing to notice is that we have CMD ["google.com"] in ec file. This defines google.com as the default argument for the ping command (if used with ENTRYPOINT). But since --entrypoint is used in the docker run command, CMD won't be used in this case.**    

---

## **CMD vs ENTRYPOINT**

While both `CMD` and `ENTRYPOINT` define what commands should run in a container, their purposes differ:

| **Aspect**              | **`CMD`**                                                                                             | **`ENTRYPOINT`**                                                                                  | **`RUN`**                                                                                          |
|--------------------------|-------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| **Purpose**             | Specifies the default command to execute when the container starts.                                   | Specifies the command that will always execute when the container starts (immutable part).        | Executes commands during the image build process.                                                  |
| **Execution Context**   | Runs when a container is started.                                                                    | Runs when a container is started.                                                                | Runs during the **image build** phase (at build time).                                              |
| **Default Behavior**    | Can be overridden by the user at runtime (`docker run <image> <command>`).                            | Cannot be fully overridden by the user unless `--entrypoint` is specified.                       | Used for preparing the image (e.g., installing dependencies, setting up the environment).          |
| **Command Type**        | Acts as the default "runtime" command for the container.                                              | Acts as the "always executed" entrypoint for the container.                                       | Executes commands to modify the image layers during build time.                                    |
| **Form Supported**      | Supports **shell form** and **exec form**.                                                           | Supports **exec form** only.                                                                      | Supports **shell form** and **exec form**.                                                         |
| **Overriding Behavior** | User can replace it entirely at runtime.                                                             | User can only append arguments to it at runtime (unless overridden explicitly with `--entrypoint`). | Once executed during image build, the result is baked into the image.                             |
| **Common Use Cases**    | Specify the default script or command to run, such as starting an app server.                        | Used for setting up an entry point (e.g., a wrapper script or command) that runs regardless of additional parameters. | Install dependencies, set up the environment, and make the image production-ready.                |
| **Example (Exec Form)** | `CMD ["python", "app.py"]`                                                                            | `ENTRYPOINT ["python", "app.py"]`                                                                | `RUN apt-get update && apt-get install -y python3`                                                 |
| **Example (Shell Form)**| `CMD python app.py`                                                                                   | Not supported.                                                                                    | `RUN apt-get update && apt-get install -y python3`                                                 |
| **Chaining with CMD**   | Only one `CMD` instruction is allowed per Dockerfile (the last one overrides previous ones).          | Can be combined with `CMD` to provide default arguments (e.g., `CMD ["arg1", "arg2"]`).           | Multiple `RUN` instructions are allowed, and each creates a new layer in the image.               |
| **When to Use**         | When you want a default command that users can override at runtime.                                   | When you want to ensure a specific command or script is always executed for the container.         | When you need to execute commands during the build phase to bake results into the image.           |

---

## **Common Docker Commands**

### **Container Management**
- **List all containers (including stopped ones)**: `docker ps -a`
- **Inspect container metadata**: `docker inspect <container_id>` or `docker inspect <image_id>`
- **List running processes in a container**: `docker top <container_id>`
- **Stop a specific container**: `docker stop <container_id>`
- **Start a stopped container**: `docker start <container_id>`
- **Stop all running containers (quietly)**: `docker stop $(docker ps -q)`
- **Remove all running and stopped containers (quietly)**: `docker rm -f $(docker ps -aq)` **Only for practicing**
- **Restart a container**: `docker restart <container_id>`
- **Delete a specific container**: `docker rm <container_id>`
- **Delete all stopped containers**: `docker container prune`
- **View aliases/options(flags) present for a specific command**: Ex: `docker image --help`, `docker rm --help` etc., **Useful Command** 

### **Image Management**
- **Dangling images**: Images that are no longer tagged or associated with any container.
- **Delete a specific image**: `docker rmi <image_id>`
- **Delete all unused images (including dangling images)**: `docker image prune -a`

---

### **Conclusion**
Understanding how to use custom-named Dockerfiles and the `docker build` command gives you greater flexibility in managing containerized applications. By mastering `CMD` and `ENTRYPOINT`, you'll better control container behavior, and by leveraging Docker commands effectively, you'll improve the efficiency of both development and deployment workflows. Keep exploring these concepts to build scalable, modular, and well-optimized Docker environments!

For further reading: [Docker Best Practices: Choosing Between RUN, CMD, and ENTRYPOINT](https://www.docker.com/blog/docker-best-practices-choosing-between-run-cmd-and-entrypoint/)

---
