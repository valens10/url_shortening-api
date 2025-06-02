# URL Shortener Backend

## Overview
This is the backend API for a scalable URL shortener web application built with Django and Django REST Framework. It provides authentication, URL shortening, analytics, and user management features. The API supports token-based authentication using  `JWT tokens for authenticated` and is fully documented using Swagger.

## Tech Stack
- **Backend Framework:** Django, Django REST Framework (DRF)
- **Authentication:** Token-based authentication (`JWT`)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose
- **API Documentation:** Swagger UI
- CI/CD pipeline for deployment and testing

## Features
- User Registration & Login (Token Authentication)
- Token refresh implementation
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
SECRET_KEY='django-insecuxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxbug2g(2kau&'
DATABASE_URL='postgres://postgres:admin@172.20.10.2:5432/db_shorten_url'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='693xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxrcontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxxxO4ssQ4'

SOCIAL_AUTH_GITHUB_KEY='OvxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxudCamGp'
SOCIAL_AUTH_GITHUB_SECRET='fe259750xxxxxxxxxxxxxxxxxxxxxxxxx7088'

# URLs
BASE_URL='http://localhost:8000'
FRONTEND_URL='http://localhost:4200'

```

### Apply Migrations & Start Server
```bash
python manage.py migrate
python manage.py runserver
pytest --cov=. --cov-branch --cov-report=xml
```

The API will be available at `http://127.0.0.1:8000/`

## Running with Docker
To run the backend using Docker, follow these steps:

### Build & Run Containers
```bash
docker-compose up --build -d
```

### Stop Containers
```bash
docker-compose down -v
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
- **Token Authentication (`JWT tokens for authenticated`)** for secure access
- **CORS/CSRF protection**
- Indexing
- **Input Validation** to ensure valid URL storage

## Deployment
- **Used github actions to deploy to render up on merge request to master branch
  ```
name: Url Shortener CI/CD

on:
  push:
    branches: [ "master"]
  pull_request:
    branches: [ "master"]

env:
  DOCKER_IMAGE: ${{ secrets.DOCKERHUB_USERNAME }}/url-shortener
  DOCKER_TAG: ${{ github.sha }}

jobs:
  test:
    name: Run tests and collect coverage
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 2

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Check Python version
        run: python --version

      - name: Clear pip cache
        run: pip cache purge || true

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Black Formatter
        run: |
          black . --check

      - name: Run Flake8 Linter
        run: |
          flake8 .

      - name: Run tests
        env:
          DJANGO_SETTINGS_MODULE: url_shortener.settings
          DATABASE_URL: sqlite:///db.sqlite3
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          FRONTEND_URL: http://localhost:8000
          BASE_URL: http://localhost:8000
        run: |
          python manage.py migrate
          pytest --cov=. --cov-branch --cov-report=xml

      - name: Upload results to Codecov
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to DockerHub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and Push Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ${{ env.DOCKER_IMAGE }}:${{ env.DOCKER_TAG }},${{ env.DOCKER_IMAGE }}:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/master'
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
          wait-for-success: true

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Wait for Render to Warm Up
        run: sleep 15

      - name: Run Production Migrations
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          SECRET_KEY: ${{ secrets.SECRET_KEY }}
          DJANGO_SETTINGS_MODULE: url_shortener.settings
          FRONTEND_URL: ${{ secrets.FRONTEND_URL }}
          BASE_URL: ${{ secrets.BASE_URL }}
          DEBUG: "False"
        run: |
          python manage.py migrate --noinput


  ```

## Contributing
![image](https://github.com/user-attachments/assets/0260ed43-bcd6-49aa-87b1-796583ff7804)

![image](https://github.com/user-attachments/assets/84e59b67-c35e-4e88-b08f-8b677b384cb4)

![image](https://github.com/user-attachments/assets/24d35536-6512-4e95-bb80-a90703706b1a)

![image](https://github.com/user-attachments/assets/db84efa4-4781-4717-878d-ecde78403af0)

![image](https://github.com/user-attachments/assets/02902b00-bbaf-4b6d-9211-98942d73380e)

![image](https://github.com/user-attachments/assets/cbb59e4a-cc7e-4702-bd13-e357bbcc7cdd)

![image](https://github.com/user-attachments/assets/f38facee-5438-48f2-bf44-f89d5a87bef1)



## Contributing
Feel free to open issues or submit PRs for improvements.
