#!/bin/bash

# Ticket to Ride Backend Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "🚀 Ticket to Ride Backend Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed ✓"
}

# Local development deployment
deploy_local() {
    print_status "Deploying locally with Docker Compose..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_warning "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration before continuing."
        read -p "Press Enter to continue after editing .env file..."
    fi
    
    # Build and start services
    docker-compose down --remove-orphans
    docker-compose build --no-cache
    docker-compose up -d
    
    print_status "Local deployment complete!"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Health Check: http://localhost:8000/health"
}

# Production deployment
deploy_production() {
    print_status "Deploying to production..."
    
    # Check for production .env file
    if [ ! -f .env.production ]; then
        print_error "Production environment file (.env.production) not found!"
        print_error "Please create .env.production with your production configuration."
        exit 1
    fi
    
    # Use production environment
    cp .env.production .env
    
    # Build production image
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
    
    # Deploy with production configuration
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    print_status "Production deployment complete!"
}

# Build Docker image for external deployment
build_image() {
    print_status "Building Docker image..."
    
    # Generate a tag with timestamp
    TAG="ticket-to-ride-backend:$(date +%Y%m%d-%H%M%S)"
    
    docker build -t $TAG .
    docker tag $TAG ticket-to-ride-backend:latest
    
    print_status "Docker image built successfully!"
    print_status "Image tag: $TAG"
    print_status "Latest tag: ticket-to-ride-backend:latest"
    
    # Show image size
    docker images ticket-to-ride-backend --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Run tests in Docker container
    docker-compose run --rm app python -m pytest test_api_comprehensive.py -v
    
    print_status "Tests completed!"
}

# Clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    docker-compose down --remove-orphans
    docker system prune -f
    
    print_status "Cleanup complete!"
}

# Show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f app
}

# Main menu
show_menu() {
    echo ""
    echo "Select deployment option:"
    echo "1) Deploy locally (Docker Compose)"
    echo "2) Deploy to production"
    echo "3) Build Docker image only"
    echo "4) Run tests"
    echo "5) Show logs"
    echo "6) Cleanup"
    echo "7) Exit"
    echo ""
}

# Main script logic
main() {
    check_docker
    
    while true; do
        show_menu
        read -p "Enter your choice (1-7): " choice
        
        case $choice in
            1)
                deploy_local
                ;;
            2)
                deploy_production
                ;;
            3)
                build_image
                ;;
            4)
                run_tests
                ;;
            5)
                show_logs
                ;;
            6)
                cleanup
                ;;
            7)
                print_status "Goodbye! 👋"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please try again."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
