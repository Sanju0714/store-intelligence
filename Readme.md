# Store Intelligence Dashboard

A real-time Store Intelligence Dashboard built using FastAPI, Streamlit, Docker, and YOLOv8 for monitoring retail analytics and customer movement insights.

## Features

* Real-time store occupancy tracking
* Entry, exit, and re-entry analytics
* Zone-wise customer analytics
* Billing metrics monitoring
* FastAPI backend APIs
* Streamlit interactive dashboard
* Docker containerized deployment
* YOLOv8-based detection pipeline

## Tech Stack

* Python
* FastAPI
* Streamlit
* Docker
* YOLOv8
* OpenCV
* Pandas
* SQLAlchemy

## Project Structure

```bash
store-intelligence/
│
├── app/
├── configs/
├── data/
├── docs/
├── output/
├── pipeline/
├── tests/
├── dashboard.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── DESIGN.md
└── CHOICES.md
```

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/store-intelligence.git
cd store-intelligence
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Project Using Docker

```bash
docker compose up --build
```

## API Documentation

Open:

```bash
http://localhost:8000/docs
```

## Dashboard

Open:

```bash
http://localhost:8501
```

## Available API Endpoints

* `/metrics/summary`
* `/metrics/zones`
* `/metrics/billing`
* `/metrics/staff`
* `/health`

## Author

Sanjana
