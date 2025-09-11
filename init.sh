#!/bin/bash
# Prepare
rm -rf services
# 1. Verify docker is installed, if not install it

# Use a variable based on docker --version exit status
DOCKER_STATUS=$(docker --version >/dev/null 2>&1 && echo "installed" || echo "missing")

if [ "$DOCKER_STATUS" = "installed" ]; then
    echo "✅ Docker is installed"
else
    echo "⌛ Docker no está instalado. Instalando..."
    # uninstall all conflicting packages
    for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update

    # 1.2. Install docker packages
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    echo "✅ Docker instalado correctamente"
fi

echo "⌛ Creando estructura del proyecto"
mkdir services
cd services
mkdir frontend && mkdir backend
git clone -b main https://github.com/cris-dangithub/oica-steel-cutting-optimizer.git backend
echo "✅ OICA Steel Cutting Optimizer clonado exitosamente"
git clone -b main https://github.com/cris-dangithub/tesis-frontend.git frontend
echo "✅ Frontend clonado exitosamente"
cd ..

# Start services
docker compose up -d --build
echo "✅ Servicios iniciados exitosamente"





# # Update system packages
# echo "📦 Updating system packages..."
# sudo apt update && sudo apt upgrade -y

# # Install required dependencies
# echo "🔧 Installing required dependencies..."
# sudo apt install -y git curl wget docker.io docker-compose

# # Start Docker service
# echo "🐳 Starting Docker service..."
# sudo service docker start

# # Create services directory if it doesn't exist
# echo "📁 Creating directory structure..."
# mkdir -p services
# mkdir -p app/data

# # Remove existing repositories if they exist (for clean reinstall)
# echo "🧹 Cleaning existing repositories..."
# if [ -d "services/backend" ]; then
#     rm -rf services/backend
# fi
# if [ -d "services/frontend" ]; then
#     rm -rf services/frontend
# fi

# # Clone backend repository
# echo "⬇️  Downloading backend repository..."
# cd services
# git clone https://github.com/cris-dangithub/oica-steel-cutting-optimizer.git backend
# cd backend
# git checkout main
# cd ../..

# # Clone frontend repository
# echo "⬇️  Downloading frontend repository..."
# cd services
# git clone https://github.com/cris-dangithub/tesis-frontend.git frontend
# cd frontend
# git checkout main
# cd ../..

# # Verify directory structure
# echo "✅ Verifying directory structure..."
# if [ -d "services/backend" ] && [ -d "services/frontend" ] && [ -d "app/data" ]; then
#     echo "   ✓ services/backend exists"
#     echo "   ✓ services/frontend exists"
#     echo "   ✓ app/data exists"
# else
#     echo "❌ Error: Directory structure not created correctly"
#     exit 1
# fi

# # Check if docker-compose.yaml exists
# if [ ! -f "docker-compose.yaml" ] && [ ! -f "docker-compose.yml" ]; then
#     echo "⚠️  Warning: No docker-compose file found in current directory"
#     echo "   Make sure you have a docker-compose.yaml file before running this script"
# else
#     echo "🐳 Found Docker Compose configuration"
# fi

# # Build and run Docker containers
# echo "🚢 Building and starting Docker containers..."
# # Note: User might need to logout and login again for docker group membership to take effect
# # For now, we'll use sudo
# if groups $USER | grep -q docker; then
#     docker compose up -d --build
# else
#     echo "ℹ️  Running Docker Compose with sudo (docker group membership not yet active)"
#     sudo docker compose up -d --build
# fi

# echo ""
# echo "🎉 Environment initialization completed successfully!"
# echo ""
# echo "📂 Created structure:"
# echo "   app/"
# echo "   ├── data/"
# echo "   services/"
# echo "   ├── backend/ (oica-steel-cutting-optimizer)"
# echo "   └── frontend/ (tesis-frontend)"
# echo ""
# echo "🐳 Docker containers are now running"
# echo ""
# echo "⚠️  Note: If you encounter docker permission issues, you may need to:"
# echo "   1. Logout and login again to activate docker group membership"
# echo "   2. Or restart your WSL instance: wsl --shutdown (from Windows) then restart"
# echo ""
# echo "✅ Setup complete! Your development environment is ready."