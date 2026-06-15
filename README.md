# SSP Product Service

This service is the source of truth for the product catalog in the Smart Shop Platform. It manages product details, pricing, and image URLs.

## Core Responsibilities & Features

1.  **Product Catalog Management:**
    *   Provides RESTful API endpoints for creating, reading, and (conceptually) updating and deleting products.
    *   Stores product data in a NoSQL database (MongoDB) which allows for flexible product schemas (e.g., adding arbitrary specifications or attributes later).

2.  **Image Handling:**
    *   Handles `multipart/form-data` uploads for product images.
    *   Securely uploads the image files to an Amazon S3 bucket, generates a unique filename, and stores the resulting public S3 URL in the product database record.

3.  **Pricing Logic:**
    *   Handles calculating the final `selling_price` based on the Maximum Retail Price (`mrp`) and an optional `discount_percent`.

4.  **Database Initialization:**
    *   On startup, the service automatically connects to MongoDB and ensures that necessary indexes (like making the product `id` unique) are created.

## Architecture
- **Framework:** **FastAPI**
- **Database:** **MongoDB** (provisioned via Amazon DocumentDB).
- **Storage:** **Amazon S3** (for product images).
- **Deployment:** **AWS ECS Fargate**
- **Dependencies:**
    - `motor`: The official asynchronous Python driver for MongoDB.
    - `boto3`: To interact with AWS S3 for uploads and AWS SSM for configuration.

## Local Development

1.  Create a virtual environment: `python3 -m venv venv`
2.  Activate it: `source venv/bin/activate`
3.  Install dependencies: `pip install -r requirements.txt` and `pip install -r requirements-dev.txt`
4.  **Set Up Local Database:** This service requires a running MongoDB instance. Start one with Docker:
    ```bash
    docker run --name ssp-mongo -p 27017:27017 -d mongo
    ```
5.  Run the application:
    ```bash
    uvicorn app.main:app --reload --port 8002
    ```
