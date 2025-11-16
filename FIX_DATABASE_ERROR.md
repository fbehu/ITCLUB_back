# Fix: "relation chat_message does not exist" Error

## Problem
When accessing the messages API endpoint, you get this error:
```
relation "chat_message" does not exist
LINE 1: ...e"."created_at", "chat_message"."updated_at" FROM "chat_mess...
```

## Root Cause
The `apps/chat` application was recently added to the project. The migration files exist in the code but haven't been executed on the production PostgreSQL database yet.

## Solution

### Option 1: Quick Command (Recommended)

SSH into your server and run these commands:

```bash
cd /path/to/ITCLUB_back
source venv/bin/activate
python manage.py migrate
sudo systemctl restart gunicorn  # or your service name
```

### Option 2: Using the Provided Script

```bash
cd /path/to/ITCLUB_back
chmod +x apply_migrations.sh
./apply_migrations.sh
sudo systemctl restart gunicorn  # or your service name
```

### Option 3: Step-by-Step Manual Process

1. **SSH into server:**
   ```bash
   ssh user@91.210.106.114
   ```

2. **Navigate to project:**
   ```bash
   cd /path/to/ITCLUB_back
   ```

3. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

4. **Install PostgreSQL driver (if needed):**
   ```bash
   pip install psycopg2-binary
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Verify migrations applied:**
   ```bash
   python manage.py showmigrations chat
   ```
   
   Should show:
   ```
   chat
    [X] 0001_initial
    [X] 0002_rename_messages_me_admin_i_idx_chat_messag_admin_i_5a5069_idx_and_more
   ```

7. **Restart Django application:**
   ```bash
   # For gunicorn
   sudo systemctl restart gunicorn
   
   # For supervisor
   sudo supervisorctl restart gunicorn
   
   # For docker
   docker-compose restart web
   ```

8. **Test the API:**
   ```bash
   curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## What Gets Created

The migrations create:

1. **Table:** `chat_message` with columns:
   - `id` (UUID primary key)
   - `text` (message content)
   - `admin_id` (foreign key to user)
   - `student_id` (foreign key to user)
   - `sender_id` (foreign key to user)
   - `file` (optional file attachment)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

2. **Indexes:** For performance optimization on frequently queried fields

## Troubleshooting

### Error: "relation already exists"
```bash
python manage.py migrate chat --fake
```

### Error: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Error: "Permission denied"
```bash
sudo -u www-data python manage.py migrate
```

### Error: "Database connection refused"
Check your database credentials in `config/settings.py` and verify PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

## Verification

After running migrations, verify the fix:

```bash
# Check if table exists
psql -U root -d itclubbase -c "\dt chat_message"

# Or test via API
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

You should get a 200 response with an empty array `[]` or messages.

## Files Provided

- **SERVER_DEPLOYMENT_GUIDE.md** - Comprehensive deployment guide
- **apply_migrations.sh** - Automated migration script
- **RUN_MIGRATIONS_ON_SERVER.md** - Detailed migration instructions

## Next Steps

1. Run the migrations on the production server
2. Restart the Django application
3. Test the API endpoints
4. Monitor logs for any issues
5. Verify file uploads work correctly

---

**Status:** Ready to deploy
**Last Updated:** November 17, 2025
