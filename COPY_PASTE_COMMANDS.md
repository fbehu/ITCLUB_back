# Copy-Paste Commands to Fix the Error

## The Error
```
relation "chat_message" does not exist
```

## The Fix (Copy and Paste These Commands)

### Step 1: SSH into your server
```bash
ssh user@91.210.106.114
```

### Step 2: Navigate to project directory
```bash
cd /path/to/ITCLUB_back
```

**Note:** Replace `/path/to/ITCLUB_back` with your actual project path. Common paths:
- `/home/user/ITCLUB_back`
- `/var/www/ITCLUB_back`
- `/opt/ITCLUB_back`

### Step 3: Activate virtual environment
```bash
source venv/bin/activate
```

### Step 4: Install PostgreSQL driver
```bash
pip install psycopg2-binary
```

### Step 5: Run migrations
```bash
python manage.py migrate
```

### Step 6: Verify migrations
```bash
python manage.py showmigrations chat
```

### Step 7: Restart Django application

**If using gunicorn with systemd:**
```bash
sudo systemctl restart gunicorn
```

**If using supervisor:**
```bash
sudo supervisorctl restart gunicorn
```

**If using docker-compose:**
```bash
docker-compose restart web
```

**If running manually:**
```bash
# Stop the current process (Ctrl+C if running in terminal)
# Then restart it
python manage.py runserver 0.0.0.0:8000
```

### Step 8: Test the API
```bash
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Replace `YOUR_TOKEN` with an actual JWT token.

---

## All Commands in One Block

If you want to run everything at once:

```bash
ssh user@91.210.106.114 && \
cd /path/to/ITCLUB_back && \
source venv/bin/activate && \
pip install psycopg2-binary && \
python manage.py migrate && \
python manage.py showmigrations chat && \
sudo systemctl restart gunicorn
```

---

## Expected Output

### After `python manage.py migrate`:
```
Operations to perform:
  Apply all migrations: admin, auth, chat, contenttypes, sessions, token_blacklist, users
Running migrations:
  Applying chat.0001_initial... OK
  Applying chat.0002_rename_messages_me_admin_i_idx_chat_messag_admin_i_5a5069_idx_and_more... OK
```

### After `python manage.py showmigrations chat`:
```
chat
 [X] 0001_initial
 [X] 0002_rename_messages_me_admin_i_idx_chat_messag_admin_i_5a5069_idx_and_more
```

### After `curl` test:
```json
[]
```
(Empty array if no messages, or array of messages if they exist)

---

## If Something Goes Wrong

### Error: "No such file or directory"
Make sure you're in the correct directory:
```bash
pwd  # Shows current directory
ls   # Lists files in current directory
```

### Error: "command not found: python"
Try using `python3` instead:
```bash
python3 manage.py migrate
```

### Error: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Error: "Permission denied"
Use sudo:
```bash
sudo python manage.py migrate
```

### Error: "Database connection refused"
Check if PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

---

## Quick Verification

After everything is done, verify it works:

```bash
# Check if migrations are applied
python manage.py showmigrations chat

# Test the API
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

If you get a 200 response with `[]` or messages, the fix is successful!

---

## Need Help?

If you're stuck:

1. Check the error message carefully
2. Make sure you're in the right directory (`pwd`)
3. Make sure virtual environment is activated (you should see `(venv)` in your terminal)
4. Check if PostgreSQL is running
5. Review the troubleshooting section above
6. Check the detailed guides:
   - `SERVER_DEPLOYMENT_GUIDE.md`
   - `FIX_DATABASE_ERROR.md`

---

**Last Updated:** November 17, 2025
