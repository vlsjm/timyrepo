# PostgreSQL Setup Guide

This project has been converted from SQLite to PostgreSQL. Follow these steps to set up your local environment.

## Prerequisites

- PostgreSQL installed and running on your system
- Python virtual environment activated

## Setup Steps

### 1. Install PostgreSQL (if not already installed)

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run the installer and note your password for the `postgres` user
- Default port: 5432

**Mac:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

### 2. Create Database and User

Open PostgreSQL command line (psql) and run:

```sql
-- Create database
CREATE DATABASE internshiptracker;

-- Create user (optional, or use default postgres user)
CREATE USER intern_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
ALTER ROLE intern_user SET client_encoding TO 'utf8';
ALTER ROLE intern_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE intern_user SET default_transaction_deferrable TO on;
ALTER ROLE intern_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE internshiptracker TO intern_user;
ALTER DATABASE internshiptracker OWNER TO intern_user;
```

Or use the default `postgres` user (simpler for development):
```sql
CREATE DATABASE internshiptracker;
```

### 3. Update .env File

Edit `.env` in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database Configuration
DB_NAME=internshiptracker
DB_USER=postgres          # or your custom user
DB_PASSWORD=              # leave empty for local dev with postgres user, or set your password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Verify Database Connection

```bash
python manage.py dbshell
```

This will open a PostgreSQL shell if the connection is successful.

### 5. Run Migrations

Create fresh migrations for PostgreSQL:

```bash
# Make fresh migrations (optional - only if schema changed)
python manage.py makemigrations

# Apply all migrations
python manage.py migrate
```

### 6. Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Start Development Server

```bash
python manage.py runserver
```

## Migration from SQLite to PostgreSQL

If you have existing SQLite data you want to preserve:

### Option A: Export/Import Data

1. **Dump data from SQLite** (before switching to PostgreSQL):
   ```bash
   python manage.py dumpdata > data.json
   ```

2. **Set up PostgreSQL** (follow steps 1-3 above)

3. **Load data into PostgreSQL**:
   ```bash
   python manage.py migrate
   python manage.py loaddata data.json
   ```

### Option B: Start Fresh

If you don't need the old data, simply follow steps 1-7 above. The migrations will create the schema from scratch.

## Troubleshooting

### Connection refused
- Ensure PostgreSQL is running
- Check DB_HOST and DB_PORT are correct
- Run: `psql -U postgres -h localhost` to test connection

### "role does not exist"
- Create the user as shown in step 2
- Or use the default `postgres` user

### "database does not exist"
- Create the database as shown in step 2

### psycopg2 import error
- Ensure psycopg2-binary is installed: `pip install -r requirements.txt`

## Switching Back to SQLite (if needed)

To temporarily switch back to SQLite for testing:

1. Update `config/settings.py` DATABASES:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

2. Run migrations: `python manage.py migrate`

## Production Deployment

For production, ensure:
- Set `DEBUG=False` in `.env`
- Use a strong `SECRET_KEY`
- Set `DB_PASSWORD` to a secure password
- Use environment-specific `.env` files
- Enable `CSRF_COOKIE_SECURE=True` with HTTPS
- Use connection pooling (pgbouncer) for high traffic
