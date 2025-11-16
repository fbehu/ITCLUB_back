# Postman Guide - Testing Message API

## Setup

### Step 1: Create Environment Variable

1. Click **Environments** (left sidebar)
2. Click **Create New**
3. Name it: `ITCLUB`
4. Add variables:
   - `base_url` = `http://91.210.106.114:8000/api`
   - `access_token` = (leave empty for now)
   - `admin_id` = `dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c`
   - `student_id` = (your student UUID)
5. Click **Save**

### Step 2: Select Environment

In the top-right corner, select `ITCLUB` from the environment dropdown.

---

## Test 1: Login (Get Access Token)

### Create Request

1. Click **New** → **Request**
2. Name: `Login`
3. Method: **POST**
4. URL: `{{base_url}}/users/login/`

### Headers

| Key | Value |
|-----|-------|
| Content-Type | application/json |

### Body (raw JSON)

```json
{
  "username_or_phone": "your_username_or_phone",
  "password": "your_password"
}
```

### Send

Click **Send**

### Extract Token

1. In the response, find the `access` field
2. Copy the token value
3. Go to **Environments** → **ITCLUB**
4. Paste it in `access_token` variable
5. Click **Save**

---

## Test 2: Send Text Message

### Create Request

1. Click **New** → **Request**
2. Name: `Send Text Message`
3. Method: **POST**
4. URL: `{{base_url}}/message/`

### Headers

| Key | Value |
|-----|-------|
| Authorization | Bearer {{access_token}} |

### Body (Form-data)

| Key | Value | Type |
|-----|-------|------|
| text | salom | Text |
| admin_id | {{admin_id}} | Text |

### Send

Click **Send**

### Expected Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "salom",
  "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
  "student_id": null,
  "created_at": "2025-11-17T10:30:00Z",
  "file_url": null,
  "file_name": null
}
```

---

## Test 3: Send Message with File

### Create Request

1. Click **New** → **Request**
2. Name: `Send Message with File`
3. Method: **POST**
4. URL: `{{base_url}}/message/`

### Headers

| Key | Value |
|-----|-------|
| Authorization | Bearer {{access_token}} |

### Body (Form-data)

| Key | Value | Type |
|-----|-------|------|
| text | Mana fayl bilan xabar | Text |
| admin_id | {{admin_id}} | Text |
| file | [Click Select Files] | File |

**To add file:**
1. Click the **file** row
2. Change type to **File** (dropdown on right)
3. Click **Select Files**
4. Choose your PDF/image/document

### Send

Click **Send**

### Expected Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "text": "Mana fayl bilan xabar",
  "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
  "student_id": null,
  "created_at": "2025-11-17T10:31:00Z",
  "file_url": "http://91.210.106.114:8000/media/messages/document.pdf",
  "file_name": "document.pdf"
}
```

---

## Test 4: Get Messages

### Create Request

1. Click **New** → **Request**
2. Name: `Get Messages`
3. Method: **GET**
4. URL: `{{base_url}}/message/?admin_id={{admin_id}}`

### Headers

| Key | Value |
|-----|-------|
| Authorization | Bearer {{access_token}} |

### Send

Click **Send**

### Expected Response

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "salom",
    "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
    "student_id": null,
    "sender_name": "Student Name",
    "created_at": "2025-11-17T10:30:00Z",
    "file_url": null,
    "file_name": null
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "text": "Mana fayl bilan xabar",
    "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
    "student_id": null,
    "sender_name": "Student Name",
    "created_at": "2025-11-17T10:31:00Z",
    "file_url": "http://91.210.106.114:8000/media/messages/document.pdf",
    "file_name": "document.pdf"
  }
]
```

---

## Test 5: Admin Sending to Student

### Create Request

1. Click **New** → **Request**
2. Name: `Admin Send to Student`
3. Method: **POST**
4. URL: `{{base_url}}/message/`

### Headers

| Key | Value |
|-----|-------|
| Authorization | Bearer {{access_token}} |

### Body (Form-data)

| Key | Value | Type |
|-----|-------|------|
| text | Salom talaba | Text |
| student_id | {{student_id}} | Text |

### Send

Click **Send**

---

## Test 6: Admin Sending with File

### Create Request

1. Click **New** → **Request**
2. Name: `Admin Send with File`
3. Method: **POST**
4. URL: `{{base_url}}/message/`

### Headers

| Key | Value |
|-----|-------|
| Authorization | Bearer {{access_token}} |

### Body (Form-data)

| Key | Value | Type |
|-----|-------|------|
| text | Mana topshiriq | Text |
| student_id | {{student_id}} | Text |
| file | [Select file] | File |

### Send

Click **Send**

---

## Organize Requests in Folders

1. Click **New** → **Folder**
2. Name: `Message API`
3. Drag all message requests into this folder

Your collection should look like:
```
Message API
├── Login
├── Send Text Message
├── Send Message with File
├── Get Messages
├── Admin Send to Student
└── Admin Send with File
```

---

## Using Pre-request Scripts

### Auto-extract Token

For the **Login** request:

1. Click **Pre-request Script** tab
2. Add:
```javascript
// Nothing needed here
```

3. Click **Tests** tab
4. Add:
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
    console.log("Token saved!");
}
```

Now when you run Login, the token is automatically saved!

---

## Using Tests for Validation

### For Send Message Request

1. Click **Tests** tab
2. Add:
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has id", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
});

pm.test("Text matches", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.text).to.equal("salom");
});
```

3. Click **Send**
4. Check the **Tests** tab in response to see results

---

## Troubleshooting in Postman

### Issue: "Authorization credentials were not provided"

**Fix:**
1. Make sure you're logged in first (run Login request)
2. Check that `access_token` is set in environment
3. Verify Authorization header is: `Bearer {{access_token}}`

### Issue: "admin_id yoki student_id ni jo'natish majburiy"

**Fix:**
1. Check Body tab is set to **Form-data**
2. Make sure both `text` and `admin_id` (or `student_id`) are present
3. Don't use JSON format for this endpoint

### Issue: File not uploading

**Fix:**
1. Change file field type to **File** (not Text)
2. Click **Select Files** button
3. Choose a valid file
4. Make sure file is < 50MB
5. File format must be: .pdf, .png, .jpg, .jpeg, .docx, .xlsx

### Issue: "Fayl hajmi 50MB dan oshmasligi kerak"

**Fix:**
Your file is too large. Maximum is 50MB.

---

## Quick Checklist

Before testing:
- [ ] Environment created with variables
- [ ] `base_url` set correctly
- [ ] Logged in and `access_token` saved
- [ ] `admin_id` or `student_id` set in environment
- [ ] Using correct HTTP method (POST/GET)
- [ ] Headers include Authorization
- [ ] Body is Form-data (not JSON)

---

## Export Collection

To share with team:

1. Click **...** next to collection name
2. Click **Export**
3. Choose **Collection v2.1**
4. Click **Export**
5. Share the JSON file

---

## Import Collection

If you have a collection file:

1. Click **Import** (top-left)
2. Select the JSON file
3. Click **Import**
4. Update environment variables
5. Ready to use!

---

## Tips & Tricks

### Tip 1: Use Variables
Instead of hardcoding values, use `{{variable_name}}`

### Tip 2: Save Responses
Click **Save Response** to save response for reference

### Tip 3: Use Collections
Organize related requests in folders

### Tip 4: Use Environments
Keep different configs (dev, staging, prod)

### Tip 5: Use Tests
Validate responses automatically

---

**Last Updated:** November 17, 2025
