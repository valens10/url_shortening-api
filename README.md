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
DATABASE_URL='postgres://[DB_USER]:[DB_PASSWORD]@[DB_HOST]:[DB_PORT]/[DB_NAME]'
#DATABASE_URL='postgres://[DB_USER]:[DB_PASSWORD]@host.docker.internal:[DB_PORT]/[DB_NAME]'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='69382xxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='GOxxxxxxxxxxxxxxxxxxxO4ssQ4'
SOCIAL_AUTH_GITHUB_KEY='Ov2xxxxxxxxxxxxxxxxxdCamGp'
SOCIAL_AUTH_GITHUB_SECRET='fe25975xxxxxxxxxxxxxxxxx049d7862f7088'

```

### Apply Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver # py .\manage.py runserver on windows
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

#### Google Login:
1. Go to the [Google Developer Console](https://console.cloud.google.com/).
2. Create a new OAuth 2.0 Client ID.
3. Set the **Authorized redirect URIs** to:
   - `http://localhost:8000/social/complete/google-oauth2/`
4. Copy the **Client ID** and **Client Secret** into `.env`.

#### GitHub Login:
1. Go to the [GitHub Developer Console](https://github.com/settings/applications).
2. Create a new OAuth application.
3. Set the **Authorization callback URL** to:
   - `http://localhost:8000/social/complete/github/`
4. Copy the **Client ID** and **Client Secret** into `.env`.


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
![image](https://github.com/user-attachments/assets/0260ed43-bcd6-49aa-87b1-796583ff7804)

![image](https://github.com/user-attachments/assets/84e59b67-c35e-4e88-b08f-8b677b384cb4)

![image](https://github.com/user-attachments/assets/24d35536-6512-4e95-bb80-a90703706b1a)

![image](https://github.com/user-attachments/assets/db84efa4-4781-4717-878d-ecde78403af0)

![image](https://github.com/user-attachments/assets/02902b00-bbaf-4b6d-9211-98942d73380e)

![image](https://github.com/user-attachments/assets/cbb59e4a-cc7e-4702-bd13-e357bbcc7cdd)




## Contributing
Feel free to open issues or submit PRs for improvements.
