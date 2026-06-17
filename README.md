# Waste Management & Recycling Hub — Backend API

Back-end link: https://ecoflow-api-dab3.onrender.com

FastAPI backend connecting waste sellers with recyclers across Kenya. Part of the EcoFlow platform.

## Features
- Offer management (create, accept, reject, counter with price/quantity)
- Transaction lifecycle (7-state machine with enforced transitions)
- Real M-Pesa Daraja integration (STK Push, B2C, callbacks)
- Card payment fallback (Pesapal) — optional, requires API keys
- Configurable platform commission (5-10% via `COMMISSION_RATE`)
- Seller/recycler messaging with read tracking
- WebSocket real-time notifications
- Unread message count endpoint

## Tech Stack
- FastAPI + Python
- SQLAlchemy ORM + SQLite (dev) / PostgreSQL (prod)
- JWT auth (utility ready)
- Docker

## Getting Started

### Local
```bash
git clone https://github.com/keithkamau/ecoflow-proj-backend
cd ecoflow-proj-backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker
```bash
docker compose up -d
```

API at http://localhost:8000  
Swagger docs at http://localhost:8000/docs

## Running Tests
```bash
pytest tests/ -v --cov=app
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Root health check |
| GET | /health | Health check |
| **Offers** | | |
| POST | /api/v1/offers/ | Create offer |
| GET | /api/v1/offers/ | List offers |
| GET | /api/v1/offers/{id} | Get single offer |
| PUT | /api/v1/offers/{id} | Accept/reject an offer |
| POST | /api/v1/offers/{id}/counter | Counter an offer with new price |
| DELETE | /api/v1/offers/{id} | Delete pending offer |
| **Transactions** | | |
| POST | /api/v1/transactions/ | Create transaction from accepted offer |
| GET | /api/v1/transactions/ | List transactions |
| GET | /api/v1/transactions/{id} | Get transaction details |
| PUT | /api/v1/transactions/{id} | Update transaction status |
| **Payments** | | |
| POST | /api/v1/payments/ | Initiate payment (M-Pesa STK Push) |
| POST | /api/v1/payments/callback | M-Pesa Daraja callback |
| POST | /api/v1/payments/{id}/confirm | Manually confirm payment (dev) |
| POST | /api/v1/payments/{id}/fail | Manually fail payment (dev) |
| GET | /api/v1/payments/{transaction_id} | Get payment by transaction |
| GET | /api/v1/payments/ | List all payments |
| GET | /api/v1/payments/detail/{id} | Get payment by ID |
| GET | /api/v1/payments/{id}/status | Query M-Pesa status |
| **Messages** | | |
| POST | /api/v1/messages/ | Send a message |
| GET | /api/v1/messages/{offer_id} | Get conversation |
| GET | /api/v1/messages/unread/count | Get unread message count |
| PUT | /api/v1/messages/{id}/read | Mark message as read |
| **WebSocket** | | |
| WS | /ws/notifications | Real-time notifications |

## Transaction States
```
offer_accepted → pickup_scheduled → pickup_completed → payment_pending → completed
      ↓                 ↓                  ↓                  ↓
   cancelled        cancelled          cancelled          disputed → completed
```

## Configuration (.env)
```
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
MPESA_PASSKEY=...
MPESA_SHORTCODE=174379
MPESA_ENVIRONMENT=sandbox
COMMISSION_RATE=0.05
```

## Branch
`feature/offers-transactions`
