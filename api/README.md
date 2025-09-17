# InstaBids Management API

FastAPI backend for the InstaBids Management platform.

## Setup

### 1. Install Dependencies

```bash
cd api
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and update with your values:

```bash
cp ../.env.example .env
```

Required variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `SUPABASE_SERVICE_KEY`: Supabase service key (admin operations)
- `JWT_SECRET_KEY`: Secret key for JWT tokens (generate a secure one)

### 3. Run the API

Development mode:
```bash
uvicorn main:app --reload --port 8000
```

Production mode:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication Endpoints

### Register
```
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "user_type": "property_manager",
  "full_name": "John Doe",
  "organization_name": "Doe Properties"
}
```

### Login
```
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Refresh Token
```
POST /api/auth/refresh
{
  "refresh_token": "jwt_refresh_token_here"
}
```

### Get Current User
```
GET /api/auth/me
Headers: Authorization: Bearer <access_token>
```

## Rate Limiting

- Default: 100 requests per hour per IP
- Configurable via environment variables

## Security

- JWT tokens with 1-hour expiry
- Refresh tokens with 30-day expiry
- Password requirements: 8+ chars, uppercase, lowercase, digit
- Rate limiting on all auth endpoints
- CORS configured for frontend origins

## Testing

Run tests:
```bash
pytest tests/
```

## Directory Structure

```
api/
├── main.py           # FastAPI app entry point
├── config.py         # Configuration management
├── models/           # Pydantic models
│   └── auth.py       # Authentication models
├── routers/          # API route handlers
│   └── auth.py       # Authentication endpoints
├── services/         # Business logic
│   └── supabase.py   # Supabase client
├── middleware/       # Custom middleware
│   └── rate_limit.py # Rate limiting
└── tests/            # Test files
```