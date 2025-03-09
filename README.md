# URL Shortener Backend

## Overview
This is the backend API for a scalable URL shortener web application built with Django and Django REST Framework. It provides authentication, URL shortening, analytics, and user management features. The API supports token-based authentication using Django Rest Framework's `rest_framework.authtoken` and is fully documented using Swagger.

## Tech Stack
- **Backend Framework:** Django, Django REST Framework (DRF)
- **Authentication:** Token-based authentication (`rest_framework.authtoken`)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **API Documentation:** Swagger UI

## Features
- User Registration & Login (Token Authentication)
- URL Shortening
- Fetching User-Specific URLs
- URL Analytics (Click Tracking)
- Redirect Shortened URLs

## Installation & Setup (Local Development)

### Prerequisites
Ensure you have the following installed:
- Python (>=3.8)
- Django & Django REST Framework
- PostgreSQL
- Docker & Docker Compose (for containerized setup)

### Clone the Repository
```bash
git clone https://github.com/valens10/url_shortening-api.git
cd url_shortening-api
```

### Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Configure Environment Variables
Create a `.env` file in the project root and set the necessary environment variables:
```env
DJANGO_DEBUG=True
DATABASE_URL='postgres://DB_USER:DB_PASSWORD@[DB_HOST]:[DB_PORT]/db_shorten_url'

```

### Apply Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## Running with Docker
To run the backend using Docker, follow these steps:

### Build & Run Containers
```bash
docker-compose up --build
```

### Stop Containers
```bash
docker-compose down
```

## API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | User login & token generation |
| POST | `/auth/logout` | Logout & invalidate token |
| POST | `/auth/refresh_token` | Refresh access token |

### URL Management Endpoints
| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | `/api/shorten` | Shorten a new URL |
| GET | `/api/urls` | Retrieve user-specific URLs |
| GET | `/api/analytics/<shortUrl>` | Retrieve analytics for a shortened URL |
| GET | `/api/redirect_url/<shortUrl>` | Redirect to the original URL |

### User Management Endpoints
| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/auth/user_details/<pk>` | Retrieve user details |

## API Documentation
The API documentation is available at:
- **Swagger UI:** `http://127.0.0.1:8000/doc/`

## Security Features
- **Token Authentication (`rest_framework.authtoken`)** for secure access
- **Rate Limiting** to prevent API abuse
- **CORS & CSRF Protection**
- **Input Validation** to ensure valid URL storage

## Deployment
### Running in Production
- Set `DEBUG=False` in `.env`
- Use a production-ready database (PostgreSQL)
- Configure a WSGI server (Gunicorn/Uvicorn) for serving the app

## Contributing
Feel free to open issues or submit PRs for improvements.
