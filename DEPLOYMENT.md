# Azure Deployment Guide for WeatherApp

Since you have a **1-year free credit** on Azure and want to host this for recruiters to see, the most cost-effective and easiest way to deploy your app is using an **Azure Virtual Machine (VM)**.

Your project already has a perfect `docker-compose.yml` setup that includes the Web Server (Django/Gunicorn), Celery Workers, Redis, and MySQL. Running this on a VM means you won't have to change any of your code or architecture.

Here is the step-by-step guide to deploying your WeatherApp for free on Azure.

## 1. Create a Free Azure Virtual Machine

Azure offers a **B1s** Linux Virtual Machine that is free for 12 months.

1. Go to the [Azure Portal](https://portal.azure.com/).
2. Search for **Virtual Machines** and click **Create** > **Azure Virtual Machine**.
3. **Basics Tab:**
   - **Subscription**: Select your Free Trial / Free credits subscription.
   - **Resource Group**: Create a new one (e.g., `WeatherApp-RG`).
   - **Virtual machine name**: `weatherapp-vm`
   - **Region**: Choose a region close to you (e.g., `Central India` or `East US`).
   - **Image**: `Ubuntu Server 22.04 LTS - x64 Gen2`
   - **Size**: Select `Standard_B1s` (This is the one eligible for free tier).
   - **Authentication type**: SSH public key (Recommended) or Password.
4. **Networking Tab:**
   - Ensure you allow inbound ports: **SSH (22)** and **HTTP (80)**.
5. Review and Create the VM. Once deployed, note down the **Public IP address**.

> [!IMPORTANT]
> If you selected SSH Public Key, make sure to download the `.pem` file when prompted. You will need it to log into your server.

## 2. Connect to your VM

Open your terminal (or PowerShell) and connect to your new VM using its Public IP:

```bash
# If using a password
ssh azureuser@<YOUR_VM_PUBLIC_IP>

# If using the .pem key
ssh -i path/to/your/key.pem azureuser@<YOUR_VM_PUBLIC_IP>
```

## 3. Install Docker and Docker Compose

Once inside your VM, run these commands to install Docker:

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install docker.io -y

# Install Docker Compose
sudo apt install docker-compose-v2 -y

# Add your user to the docker group so you don't need 'sudo' for docker commands
sudo usermod -aG docker $USER
```
*(After running the `usermod` command, type `exit` to disconnect, and SSH back in for the changes to take effect).*

## 4. Clone Your Code

Now, clone your GitHub repository to the VM:

```bash
git clone https://github.com/vprayag2005/WeatherApp.git
cd WeatherApp
```

## 5. Configure Environment Variables

You need to create your `.env` file on the server.

```bash
cp .env.example .env
nano .env
```
Fill in your database credentials and any API keys needed for your Django app. Since it's for recruiters, make sure `DEBUG=False` and set `ALLOWED_HOSTS` to include your VM's Public IP.

```env
# Example .env settings
DEBUG=False
ALLOWED_HOSTS=<YOUR_VM_PUBLIC_IP>,127.0.0.1,localhost
```

## 6. Run the Application

Now, simply start your application using Docker Compose!

```bash
docker compose up -d --build
```

This will download the necessary images (MySQL, Redis, Python), build your Django app, and start all the services in the background.

## 7. Open Port 8000 on Azure (Optional but Recommended)

In your `docker-compose.yml`, the web service is mapped to port `8000`. To access this from the internet, you need to open port 8000 in Azure:

1. Go back to your VM in the Azure Portal.
2. Click on **Networking** on the left menu.
3. Click **Add inbound port rule**.
4. Set **Destination port ranges** to `8000`.
5. Set **Protocol** to `TCP`.
6. Click **Add**.

Now, you can visit your app at: `http://<YOUR_VM_PUBLIC_IP>:8000/`

> [!TIP]
> **Next Steps for a Professional Look:**
> To really impress recruiters, consider buying a cheap domain name (e.g., from Namecheap or Cloudflare) and setting up a reverse proxy (like Nginx or Caddy) on the VM to serve your app on standard port 80 and add free HTTPS (SSL) via Let's Encrypt!
