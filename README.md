# FastAPI SQL Auth API

This REST API was developed using **FastAPI**, JWT authentication, **PostgreSQL** persistence, **Amazon S3** file uploads, and **AWS EC2** deployment using **Docker**.

This README describes **the entire project flow**, including **local configuration**, **cloud infrastructure (AWS)**, and **security best practices**.

---

## General Architecture

```
Cliente (Web / Mobile / Insomnia)
        ↓
     EC2 (Docker)
        ↓
     FastAPI (Uvicorn)
        ↓
 ┌───────────────┐      ┌───────────────┐
 │ PostgreSQL    │      │ Amazon S3     │
 │ (Amazon RDS)  │      │ Avatares      │
 └───────────────┘      └───────────────┘
```

---

## Stack Used

* **Python 3.11**
* **FastAPI**
* **SQLAlchemy (async)**
* **PostgreSQL**
* **JWT (Auth)**
* **Amazon S3** (file upload)
* **Amazon RDS** (managed PostgreSQL)
* **Amazon EC2** (deploy)
* **Docker & Docker Compose**

---

## Project Structure

```
fastapi-sql-auth-api/
├── api
│   └── v1
│       ├── api.py
│       └── endpoints
│           ├── article.py
│           └── user.py
├── core
│   ├── auth.py
│   ├── configs.py
│   ├── database.py
│   ├── deps.py
│   └── security.py
├── create_tables.py
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── main.py
├── models
│   ├── __all_models.py
│   ├── article_model.py
│   └── user_model.py
├── README.md
├── requirements.txt
├── schemas
│   ├── article_schema.py
│   ├── user_mapper.py
│   └── user_schema.py
└── services
    └── s3_service.py
```

---

## Environment Variables

Create afile `.env` based on `.env.example`.

```env
API_V1_STR=/api/v1
DB_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB_NAME
JWT_SECRET=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
```

**Never version actual `.env` files.**

---

## Amazon S3 Configuration

### 1 Create the Bucket

* Service: **Amazon S3**
* Name: `fastapi-users-assets-<unique>`
* Region: `us-east-1`
* Block public access: **SIM**

### 2 Object Structure

```
avatars/
 └── userId-uuid.ext
```

### 3 Access Policy

The API **doesn't expose objects publicly**.

Access to the files is via **Presigned URLs**, which are generated dinamically.

---

## IAM Configuration (Recommended)

### Option A — IAM User (Study / MVP)

Create a user with the following policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::fastapi-users-assets-*/*"
    }
  ]
}
```

Use the credentials in `.env`.

### Option B — IAM Role (Production)

* Create Role
* Associate with EC2
* Allow access to S3
* **Remove credentials from `.env`**

---

## Database Configuration (Amazon RDS)

### 1. Create Instance

* Engine: PostgreSQL
* Class: `db.t4g.micro`
* Storage: 20 GB
* Master User: `postgres`

### 2. Create Database

```sql.CREATE DATABASE system;```

### 3. Security Group

Allow access:

| Type       | Port  | Origin                |
| ---------- | ----- | --------------------- |
| PostgreSQL | 5432  | Security Group da EC2 |

---

## EC2 Configuration

### 1. Create Instance

* AMI: Amazon Linux 2023
* Type: t2.micro or t3.micro
* Storage: 8 GB

### 2. Security Groups

| Port  | Protocol  | Origin                 |
| ----- | --------- | ---------------------- |
| 22    | TCP       | Your IP                 |
| 8000  | TCP       | 0.0.0.0/0 (temporary) |

---

## Docker & Deploy

### Dockerfile

Responsible for building the FastAPI API.

### docker-compose.yml

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
```

### Launch the Application

```bash
docker compose up -d --build
```

---

## Tests

### Swagger

```
http://<EC2_PUBLIC_IP>:8000/docs
```

### Avatar Upload

* Method: `POST`
* Type: `multipart/form-data`
* Field: `file`

---

## Security Best Practices

* Do not expose buckets publicly
* Use Presigned URLs
* Do not version `.env` files
* Restricted Security Groups
* IAM Role in production

---

## Next Steps

* [ ] Nginx as a reverse proxy
* [ ] HTTPS with Let's Encrypt
* [ ] Custom domain
* [ ] CI/CD (GitHub Actions)
* [ ] Rate limit
* [ ] Observability

---

## Author

**Michel Bernardo**
Project focused on backend, cloud, and best production practices.

---

## License

MIT License
