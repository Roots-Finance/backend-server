# Pull the latest changes from the Git repository
git pull origin main  # Replace 'main' with your branch name if different

# Build the Docker image
docker build -t hackprinceton:latest .

# Run the Docker container
docker run --network hp_network --env-file ./.env -p 8080:8080 hackprinceton:latest

