# Waste Management & Recycling Hub — Backend API

FastAPI-based REST API for waste management platform.

## Features

- User authentication with JWT & OTP
- Waste listings & inventory management
- Offer negotiation system
- Payment processing (M-Pesa & Card)
- Pickup coordination
- Environmental impact tracking
- Real-time messaging
- Analytics & reporting

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT
- **Payment:** M-Pesa Daraja
- **Storage:** AWS S3
- **Containerization:** Docker

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Docker & Docker Compose

## Installation

### Local Setup

1. **Clone repository**

```bash
   git clone https://github.com/yourusername/waste-management-backend.git
   cd waste-management-backend
```

2. **Create virtual environment**

```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
   pip install -r requirements.txt
```

4. **Configure environment**

```bash
   cp .env.example .env
   # Edit .env with your values
```

5. **Run migrations**

```bash
   alembic upgrade head
```

6. **Start server**

```bash
   uvicorn app.main:app --reload
```

API will be at `http://localhost:8000`

### Docker Setup

```bash
docker-compose up -d
```

## API Documentation

Once running, visit:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Project Structure

app/
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── api/
│   └── v1/
│       └── endpoints/  # API routes
├── services/        # Business logic
├── utils/          # Helper functions
└── middleware/     # Custom middleware

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_auth.py::test_register_user -v
```

**Current Coverage:** 10%+ (Target: Production 80%+)

## Contributing

1. Create feature branch: `git checkout -b feature/description`
2. Make changes with descriptive commits
3. Push: `git push origin feature/description`
4. Create Pull Request
5. Await code review & approval

## Releases

Releases follow semantic versioning: `v1.0.0`

- Push release tag: `git tag -a v1.0.0 -m "Release version 1.0.0"`
- Push tags: `git push origin --tags`
- DockerHub image: `yourusername/waste-backend:v1.0.0`

## Deployment

### Production Deployment

1. **Build Docker image**

```bash
   docker build -t yourusername/waste-backend:v1.0.0 .
```

2. **Push to DockerHub**

```bash
   docker push yourusername/waste-backend:v1.0.0
```

3. **Deploy on AWS EC2**

```bash
   # SSH into server
   ssh ubuntu@your-server-ip
   
   # Pull image & run
   docker pull yourusername/waste-backend:v1.0.0
   docker run -d --name waste-backend \
     -e DATABASE_URL=postgresql://... \
     -p 8000:8000 \
     yourusername/waste-backend:v1.0.0
```

## Environment Variables

See `.env.example` for complete list. Key variables:

- `DATABASE_URL` — PostgreSQL connection string
- `SECRET_KEY` — JWT secret (change in production)
- `MPESA_CONSUMER_KEY` — M-Pesa API key
- `AWS_ACCESS_KEY_ID` — AWS S3 credentials
- `GOOGLE_MAPS_API_KEY` — Geolocation API

## Troubleshooting

**Port 8000 already in use:**

```bash
lsof -i :8000
kill -9 <PID>
```

**Database connection error:**

- Check PostgreSQL is running
- Verify `DATABASE_URL` in `.env`
- Run migrations: `alembic upgrade head`

## Support & Issues

Open issues on GitHub: [Issues](https://github.com/yourusername/waste-management-backend/issues)

## License

MIT License