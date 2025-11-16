# Server Deployment Guide - Messages API

## Problem
The error `relation "chat_message" does not exist` indicates that the database migrations haven't been applied on the production server.

## Root Cause
The `apps/chat` application was recently added to the project. The migration files exist locally but haven't been executed on the production PostgreSQL database.

## Solution

### Quick Fix (Recommended)

SSH into your production server and run:

```bash
# 1. Navigate to project directory
cd /path/to/ITCLUB_back

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run all pending migrations
python manage.py migrate

# 4. Verify the chat app migrations were applied
python manage.py showmigrations chat

# 5. Restart your Django application
# For gunicorn:
sudo systemctl restart gunicorn
# Or for other services, restart accordingly
```

### Detailed Steps

#### Step 1: Connect to Server
```bash
ssh user@91.210.106.114
# Enter your password when prompted
```

#### Step 2: Navigate to Project
```bash
cd /path/to/ITCLUB_back
# Usually something like: /home/user/ITCLUB_back or /var/www/ITCLUB_back
```

#### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
# You should see (venv) at the beginning of your terminal prompt
```

#### Step 4: Install Missing Dependencies (if needed)
```bash
pip install psycopg2-binary
```

#### Step 5: Run Migrations
```bash
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, chat, contenttypes, sessions, token_blacklist, users
Running migrations:
  Applying chat.0001_initial... OK
  Applying chat.0002_rename_messages_me_admin_i_idx_chat_messag_admin_i_5a5069_idx_and_more... OK
```

#### Step 6: Verify Migrations
```bash
python manage.py showmigrations chat
```

Expected output:
```
chat
 [X] 0001_initial
 [X] 0002_rename_messages_me_admin_i_idx_chat_messag_admin_i_5a5069_idx_and_more
```

#### Step 7: Restart Application
```bash
# If using systemd with gunicorn
sudo systemctl restart gunicorn

# If using supervisor
sudo supervisorctl restart gunicorn

# If using docker
docker-compose restart web

# If running manually, stop and restart the process
```

#### Step 8: Verify the Fix
```bash
# Test the API endpoint
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

You should get a 200 response with an empty array `[]` or messages if any exist.

---

## What Gets Created

The migrations create the following in your PostgreSQL database:

### Table: `chat_message`
```sql
CREATE TABLE chat_message (
    id UUID PRIMARY KEY,
    text TEXT NOT NULL,
    admin_id UUID REFERENCES auth_user(id),
    student_id UUID REFERENCES auth_user(id),
    sender_id UUID NOT NULL REFERENCES auth_user(id),
    file VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Indexes
```sql
CREATE INDEX chat_message_admin_created_at ON chat_message(admin_id, created_at);
CREATE INDEX chat_message_student_created_at ON chat_message(student_id, created_at);
CREATE INDEX chat_message_sender_created_at ON chat_message(sender_id, created_at);
```

---

## Troubleshooting

### Issue: "relation already exists"
If you get an error that the table already exists:
```bash
python manage.py migrate chat --fake
```

### Issue: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Issue: "Permission denied"
Make sure you're using the correct user and have proper permissions:
```bash
# Check current user
whoami

# If needed, use sudo
sudo -u www-data python manage.py migrate
```

### Issue: "Database connection refused"
Check your database credentials in `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'itclubbase',
        'USER': 'root',
        'PASSWORD': 'Cyber_992398981itclub',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
```

Verify PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

---

## Verification Checklist

After running migrations, verify everything works:

- [ ] SSH into server successfully
- [ ] Navigated to project directory
- [ ] Virtual environment activated
- [ ] `python manage.py migrate` ran successfully
- [ ] `python manage.py showmigrations chat` shows [X] for both migrations
- [ ] Application restarted
- [ ] API endpoint returns 200 status
- [ ] Can send messages via POST /api/message/
- [ ] Can retrieve messages via GET /api/message/?admin_id=...

---

## Files Involved

The following files are part of the Messages API:

```
apps/chat/
├── models.py              # Message model definition
├── serializers.py         # API serializers
├── views.py               # API views
├── urls.py                # URL routing
├── admin.py               # Django admin
└── migrations/
    ├── 0001_initial.py    # Creates chat_message table
    └── 0002_*.py          # Index renaming
```

---

## API Endpoints (After Migration)

Once migrations are applied, these endpoints will work:

### Get Messages
```
GET /api/message/?admin_id={admin_uuid}
GET /api/message/?student_id={student_uuid}
```

### Send Message
```
POST /api/message/
Content-Type: multipart/form-data

text: "Message content"
admin_id: "uuid" OR student_id: "uuid"
file: [optional file]
```

---

## Support

If you encounter any issues:

1. Check the error message carefully
2. Verify PostgreSQL is running
3. Verify database credentials
4. Check file permissions
5. Review the troubleshooting section above
6. Check Django logs for more details

---

## Next Steps

After successful migration:

1. Test the API endpoints
2. Monitor application logs
3. Verify file uploads work correctly
4. Test with actual admin and student users
5. Monitor database performance

---

**Last Updated:** November 17, 2025
**Status:** Ready for deployment
