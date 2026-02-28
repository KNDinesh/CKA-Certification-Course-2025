# Day 7: Kubernetes Architecture & Deployment Creation Workflow | CKA Certification Course 2025

## Video reference for Day 7 is the following:

[![Watch the video](https://img.youtube.com/vi/-9Cslu8PTjU/maxresdefault.jpg)](https://www.youtube.com/watch?v=-9Cslu8PTjU&ab_channel=CloudWithVarJosh)

---
## ⭐ Support the Project  
If this **repository** helps you, give it a ⭐ to show your support and help others discover it! 

---

## What is Pod?
![Alt text](/images/7a.png)

## What are **Network namespaces**?
- **Network namespaces** in Kubernetes provide an isolated network environment for each Pod. Each Pod has its own unique network namespace, which means it has its own IP address, network interfaces, and routing tables.
- All containers within a Pod share the same network namespace, meaning they can communicate with each other using **localhost** and have direct access to each other’s ports.
- This isolation ensures that Pods can communicate with each other using their internal IPs, but also keeps them separated from other Pods' networks within the cluster.



## What is a Deployment?
![Alt text](/images/7b.png)


![Alt text](/images/7f.png)
- **Deployments** wrap **ReplicaSets** to manage scaling and updates. A Deployment ensures that the desired number of Pods are running and takes care of versioning and rolling updates.
- **ReplicaSets** wrap **Pods** by maintaining a stable set of replica Pods and ensuring that the specified number of Pods are running at all times, even in case of Pod failure.
- **Pods** wrap **Containers**. A Pod is the smallest deployable unit in Kubernetes, and it contains one or more containers that share the same network namespace and storage volumes.

# Kubernetes Architecture

![Alt text](/images/7c.png)

Kubernetes operates on a master-worker architecture, where:

### Control Plane
- **Role**: This is the brain of the cluster, responsible for managing and orchestrating all the worker nodes.
- **Description**: It's a set of core components that run on a separate set of machines.

### Worker Nodes
- **Role**: These are the machines where your applications actually run.
- **Description**: They execute the instructions received from the control plane.


## Control Plane Components

1. **etcd**  
   - A distributed key-value store that stores all the cluster's configuration data.

2. **API Server**  
   - The front-end for the Kubernetes control plane.  
   - Exposes the Kubernetes API, allowing users and tools to interact with the cluster.

3. **Scheduler**  
   - Assigns Pods to worker nodes based on resource availability and other constraints.

4. **Controller Manager**  
   - Implements control loops that ensure the desired state of the cluster is maintained.  
   - Handles tasks like replication, scaling, and garbage collection.

5. **Cloud Controller Manager (CCM)**
   - Integrates Kubernetes with the cloud provider.
   - It manages cloud-specific resources and interacts with the cloud provider's API.

## Data Plane Components

1. **Kubelet**  
   - An agent that runs on each worker node.  
   - Communicates with the control plane and ensures that containers are running as expected.

2. **Kube-proxy**  
   - A network proxy that runs on each worker node.  
   - Handles network routing and service discovery within the cluster.

3. **Container Runtime**  
   - The software responsible for running containers on the worker nodes (e.g., containerd, CRI-O, Podman, Rocket).

## Control Plane vs Data Plane

| **Feature**       | **Control Plane**                                      | **Data Plane**                            |
|--------------------|-------------------------------------------------------|-------------------------------------------|
| **Responsibility** | Manages the cluster                                   | Runs applications                         |
| **Components**     | etcd, API Server, Scheduler, Controller Manager, Cloud Controller Manager | Kubelet, Kube-proxy, Container Runtime    |
| **Location**       | Typically on dedicated machines or in a highly available configuration | On each worker node                       |
| **Focus**          | Orchestration, management, and control               | Running applications and managing resources |

---

## **Kubernetes: Python Frontend, Redis Service, kube-proxy, and CNI Interaction**

![Alt text](/images/7d.png)

Let’s walk through this step by step, in simple language, but without losing the important technical details.

We’ll use your example:

   * Python frontend Pod

   * Redis exposed via a Service

   * DNS handled by CoreDNS

   * Traffic handled by kube-proxy

   * Networking provided by a CNI plugin like Calico or Flannel

🌐 Big Picture (What’s Really Happening)

When the Python frontend connects to Redis using:

      redis.default.svc.cluster.local

This is what happens behind the scenes:

   1. DNS converts name → ClusterIP
   
   2. kube-proxy converts ClusterIP → Pod IP
   
   3. CNI moves packets between Pods
   
   4. Redis replies directly

Now let’s expand each piece clearly.

1️⃣ Step 1 — DNS Resolution (CoreDNS)

The Python frontend does not know Redis Pod IPs.

It only knows the Service name:

      redis.default.svc.cluster.local

🔹 The frontend asks DNS:

* “What IP is this name?”

🔹 CoreDNS responds with:

* The Service’s ClusterIP (example: 10.96.0.25)

Important:

   **This IP is virtual**
   
   **No Pod actually owns this IP**
   
   **It represents the Service**

At this point:

Python frontend thinks it is talking to:

      10.96.0.25:6379

But that IP is not a real Pod.

That’s where kube-proxy comes in.

2️⃣ Step 2 — kube-proxy Intercepts the Traffic

* kube-proxy runs on every node.

When the frontend sends traffic to:

      Destination: 10.96.0.25:6379

kube-proxy has already installed iptables or IPVS rules on the node.

These rules say:

* “If traffic is going to this ClusterIP, redirect it to one of the real Redis Pods.”

🔁 What kube-proxy Actually Does

It checks the Service’s Endpoints object.

That object contains:

      Redis Pod 1 → 10.244.1.10
      Redis Pod 2 → 10.244.2.15
      Redis Pod 3 → 10.244.1.22

kube-proxy then:

✅ Load balances

Selects one Pod (round-robin or IPVS algorithm)

✅ Ensures Pod is healthy

Only routes to Ready Pods

✅ Rewrites the packet

It changes:

      Destination IP:
      10.96.0.25  →  10.244.1.10

Now the packet is heading to a real Redis Pod.

Important:

   * kube-proxy does NOT continuously handle packets.
   
   * It installs rules in the Linux kernel.
   
   * The kernel forwards traffic.

3️⃣ Step 3 — CNI Handles the Actual Networking

Now the packet must physically reach:

      10.244.1.10 (Redis Pod)

This is where CNI comes in.

CNI already ensured:

   * Every Pod has a unique IP
   
   * Nodes know how to route Pod CIDRs
   
   * Networking between nodes works

📍 Case A: Redis Pod on Same Node

If both frontend and Redis are on the same node:

Traffic flows like this:

      Frontend Pod
         ↓
      veth
         ↓
      Linux bridge (cni0)
         ↓
      veth
         ↓
      Redis Pod

Everything stays inside the node.

Very fast.

📍 Case B: Redis Pod on Different Node

If Redis Pod is on another node:

Traffic flows like this:

      Frontend Pod
         ↓
      Node A
         ↓
      Cluster Network
         ↓
      Node B
         ↓
      Redis Pod

How this works depends on CNI:

   * Overlay (VXLAN encapsulation)
   
   * Or BGP routing (direct routing)

But the key idea:

👉 CNI configured routing so nodes know how to reach each other’s Pod IP ranges.

After setup, the Linux kernel handles forwarding.
   
CNI is not actively moving packets.

4️⃣ Step 4 — Redis Responds

Now Redis receives the request.

It processes it and sends back a response.

Here’s something important:

🔁 The return traffic does NOT go through kube-proxy.

Why?

Because:

   * The connection is already established

   * Connection tracking remembers the original source

   * The reply goes directly back to the frontend Pod IP

The return path uses the same CNI routing setup.

🧠 Why kube-proxy Is NOT Used on Return

kube-proxy only acts when traffic is going to:

      ClusterIP

But Redis replies directly to:

      Frontend Pod IP

That is a real Pod IP.

So no Service abstraction is involved on return.

🎯 What Each Component Is Responsible For
🧩 CoreDNS

   * Converts Service name → ClusterIP

   * Purely name resolution

🚦 kube-proxy

* Watches Services & Endpoints

* Installs iptables/IPVS rules

* Performs:

   * Load balancing
   
   * Traffic redirection
   
   * Service abstraction

Acts like:

   * Traffic director for Services

🌐 CNI

   * Assigns Pod IPs

   * Creates veth pairs

   * Configures bridges or routing

   * Enables Pod-to-Pod communication

   * Enables cross-node networking

Acts like:

   The actual road system

📦 Redis Service

   * Stable virtual IP

   * Hides changing Pod IPs

   * Gives consistent DNS name

Acts like:

   A stable front door

🔄 Full Flow Summary (Very Simple Version)

1. Python asks DNS → gets ClusterIP

2. kube-proxy intercepts → chooses Redis Pod

3. CNI routes packet → reaches Redis Pod

4. Redis replies directly → back to frontend

5. kube-proxy not involved in response

## Example Flow: Communication Between Pods

Here’s an example of how two Pods (Python frontend and Redis) communicate in a Kubernetes cluster.

### Step-by-Step Flow:

1. **Python Frontend Pod Sends Request:**
   - The **Python frontend Pod** sends a request to the **Redis service** (e.g., `redis-service:6379`).

2. **kube-proxy Intercepts Traffic:**
   - **kube-proxy** intercepts the traffic and looks up the **Redis Service’s endpoints** to find a healthy Redis Pod.
   
3. **Traffic Forwarded to Redis Pod:**
   - After finding a healthy Redis Pod, **kube-proxy** forwards the request to that **Redis Pod**.

4. **Redis Pod Processes the Request:**
   - The **Redis Pod** processes the request and sends the response directly back to the **Python frontend Pod**.

This process ensures seamless communication between services in the Kubernetes cluster, with **kube-proxy** handling the routing of traffic to the appropriate Pods.

**Additional Considerations:**

* **CNI Plugins:** Some advanced CNI plugins (e.g., Calico, Cilium) can offload service-to-pod routing directly, potentially reducing kube-proxy’s role.
* **Service Type Impact:** Depending on the Service type (e.g., ClusterIP, NodePort, or LoadBalancer), the traffic path and kube-proxy’s role might differ slightly. We will discuss **Service Types** in detail in future lessons.

___

# **Kubernetes Deployment Workflow**

![Alt text](/images/7e.png)

This process outlines the steps that occur when you apply a Kubernetes Deployment, from creation to Pod scheduling and running.

## **1. User Initiates Deployment Creation**
- **Command**:  
  The user runs `kubectl apply -f python-frontend-deployment.yaml` to create a new Deployment.

- **kubectl Action**:  
  - Validates the YAML file for:
    - **Syntax** (e.g., proper formatting, indentation).
    - **Basic Kubernetes schema correctness** (e.g., valid API versions, resource definitions).
  - Sends the validated Deployment object to the **API Server**.

## **2. API Server Actions**
The API Server receives the validated Deployment object and performs the following tasks:

1. **Authentication and Authorization**:  
   Verifies that the user has the correct permissions to create the Deployment.

2. **Validation**:  
   Ensures the Deployment object conforms to the complete Kubernetes schema.

3. **Storage**:  
   - Stores the desired state of the Deployment in **etcd** (the cluster’s database).  
     *This includes details such as the Deployment's metadata, desired number of Pods, and Pod template.*

4. **Response**:  
   - Returns a success message (e.g., *"deployment created"*) to the user.

## **3. Deployment Controller Workflow**
The **Deployment Controller** is part of the Controller Manager and ensures that the desired number of Pods are running in your cluster.

### **How It Works**
1. The Deployment Controller continuously watches the API Server for any changes to Deployment objects.
2. It compares the **desired state** (e.g., number of Pods defined in the Deployment) with the **actual state** (number of Pods currently running in the cluster).

### **What Happens When Desired State Differs?**
If the actual number of Pods doesn’t match the desired state:

1. **ReplicaSet Creation**:  
   - The Deployment Controller instructs the API Server to create a **ReplicaSet object**.  
   - The API Server **stores the ReplicaSet object** in **etcd**.

2. **Pod Creation**:

   - The **ReplicaSet Controller** monitors the **ReplicaSet object** via the **API Server** (not directly in etcd).
   - If Pods are needed (e.g., scaling or Pod failure):
     - The ReplicaSet Controller instructs the **API Server** to create the required **Pod objects**.
     - The **API Server** stores the new **Pod objects** in **etcd** (the cluster’s database).
   - **Note**:
     - At this stage, only the **Pod objects** are created and stored in etcd.
     - The actual **containers** inside these Pods will be created later when the **Kubelet** starts managing the Pods on the assigned nodes.

3. **Status Update**:  
   - The Deployment Controller updates the **Deployment object** in the API Server to reflect the current state, including:
     - The number of **available Pods**: These are Pods that have been created but might not be running yet.
     - The number of **ready Pods**: These are Pods that are up and running, and their containers have passed health checks. A Pod is considered "ready" only when all of its containers are running and healthy.


## **4. Scheduler's Role**
The Scheduler is responsible for assigning unscheduled Pods (Pods without a `nodeName`) to appropriate nodes.

### **How It Works**
1. The Scheduler watches the API Server for Pod objects with no `nodeName`.
2. For each unscheduled Pod:
   - The Scheduler selects a suitable node based on:
     - **Resource availability** (e.g., CPU, memory).
     - **Node affinities** (*to be discussed later*).
     - **Taints and tolerations** (*to be discussed later*).
3. The Scheduler updates the **Pod object** in the API Server, adding the `nodeName` to indicate where the Pod will run.
4. The updated Pod object is stored in etcd via the **API Server**.

## **5. API Server Updates the Pod Status**
- The API Server receives the node selection from the Scheduler.  
- It updates the **Pod object** in **etcd** with the `nodeName` to indicate the assigned node.


## **6. Kubelet's Role**
The **Kubelet** on the assigned node monitors the API Server for changes to Pod objects.

### **How It Works**
1. The Kubelet detects the new Pod scheduled to its node by watching the **API Server**.
2. The Kubelet retrieves the **Pod object** from the **API Server**, which includes details about:
   - Container specifications.
   - Network and volume configurations.

### **Kubelet Actions**
1. **Container Runtime Interface (CRI)**:  
   The Kubelet interacts with the container runtime (e.g., `containerd`, `CRI-O`) to:
   - **Pull container images** from the registry.
   - **Configure networking** using the CNI plugin.
   - **Mount volumes** specified in the Pod definition.
   - **Create and start containers** inside the Pod.

2. **Health Monitoring**:  
   - The Kubelet continuously monitors the health of the containers and updates their status in the API Server.  
   - These updates are stored in **etcd**.

## **7. Pod Running**
1. **Once the containers are running, the Pod is live on the assigned node.**  
2. **Deployment Controller:**  
   - **Manages the ReplicaSet**, ensuring it is configured to maintain the desired state.  
   - **Does not directly monitor or recreate Pods**; this is the responsibility of the ReplicaSet Controller.  
3. **ReplicaSet Controller:**  
   - **Monitors the Pods via the API Server.**  
   - If a **Pod fails or is terminated**, the ReplicaSet Controller detects the discrepancy and takes action to **recreate the missing Pod** to maintain the desired state.  
4. **Key Points:**  
   - The **Kubelet monitors the containers' health** and status on the assigned node.  
   - It **reports the containers' running status** to the API Server.  
   - The **API Server updates the Pod's status** in etcd to reflect the current state of the containers.  
---

### Additional Resources

Kubernetes Documentation: [[Kubernetes Architecture](https://kubernetes.io/docs/concepts/architecture/)]
