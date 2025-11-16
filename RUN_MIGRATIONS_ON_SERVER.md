# Running Migrations on Production Server

The error `relation "chat_message" does not exist` means the database table hasn't been created yet on the production server.

## Solution

You need to run the migrations on the production server where the PostgreSQL database is running.

### Step 1: SSH into the server
```bash
ssh user@91.210.106.114
```

### Step 2: Navigate to the project directory
```bash
cd /path/to/ITCLUB_back
```

### Step 3: Activate virtual environment
```bash
source venv/bin/activate
```

### Step 4: Run migrations
```bash
python manage.py migrate
```

Or specifically for the chat app:
```bash
python manage.py migrate chat
```

### Step 5: Verify migrations were applied
```bash
python manage.py showmigrations chat
```

You should see:
```
chat
 [X] 0001_initial
 [X] 0002_rename_messages_me_admin_i_idx_chat_messag_admin_i_5a5069_idx_and_more
```

### Step 6: Restart the Django application
```bash
# If using gunicorn
sudo systemctl restart gunicorn

# If using another service, restart accordingly
```

---

## What the migrations do

**0001_initial.py:**
- Creates the `chat_message` table
- Adds columns: id, text, admin_id, student_id, sender_id, file, created_at, updated_at
- Creates foreign key relationships to the User model
- Creates database indexes for performance

**0002_*.py:**
- Renames the indexes to match the new app name (chat instead of messages)

---

## If migrations fail

If you get an error like "relation already exists", it means the table was created with the old app name. In that case:

```bash
# Check the current migration state
python manage.py showmigrations

# If needed, you can fake the migration
python manage.py migrate chat --fake
```

---

## Verification

After running migrations, test the API:

```bash
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer {your_token}"
```

You should get a 200 response with an empty array or messages.
