# Testing Message API - POST Request Guide

## Overview
The `/api/message/` endpoint accepts POST requests to send messages between students and admins. You can send:
- Text-only messages
- Messages with file attachments

---

## Prerequisites

1. **Valid JWT Token** - Get this from login endpoint
2. **Admin UUID** - The UUID of the admin you want to message
3. **Student UUID** - The UUID of the student you want to message
4. **Content-Type** - Must be `multipart/form-data` (for file support)

---

## Test 1: Send Text-Only Message (Student to Admin)

### Using cURL

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

### Using Postman

1. **Method:** POST
2. **URL:** `http://91.210.106.114:8000/api/message/`
3. **Headers:**
   - `Authorization: Bearer YOUR_ACCESS_TOKEN`
4. **Body:** Form-data
   - Key: `text` | Value: `salom` | Type: Text
   - Key: `admin_id` | Value: `dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c` | Type: Text

### Expected Response (201 Created)
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

## Test 2: Send Message with File (Student to Admin)

### Using cURL

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=Mana fayl bilan xabar" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -F "file=@/path/to/document.pdf"
```

### Using Postman

1. **Method:** POST
2. **URL:** `http://91.210.106.114:8000/api/message/`
3. **Headers:**
   - `Authorization: Bearer YOUR_ACCESS_TOKEN`
4. **Body:** Form-data
   - Key: `text` | Value: `Mana fayl bilan xabar` | Type: Text
   - Key: `admin_id` | Value: `dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c` | Type: Text
   - Key: `file` | Value: [Select file] | Type: File

### Expected Response (201 Created)
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

## Test 3: Admin Sending Message to Student

### Using cURL (Text Only)

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -F "text=Salom talaba" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440002"
```

### Using cURL (With File)

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -F "text=Mana sizning topshiriqlaringiz" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440002" \
  -F "file=@/path/to/assignment.pdf"
```

---

## Supported File Formats

| Format | Extension | Example |
|--------|-----------|---------|
| PDF | `.pdf` | document.pdf |
| PNG Image | `.png` | image.png |
| JPEG Image | `.jpg`, `.jpeg` | photo.jpg |
| Word Document | `.docx` | report.docx |
| Excel Spreadsheet | `.xlsx` | data.xlsx |

---

## File Size Limits

- **Maximum:** 50MB
- **Recommended:** < 10MB for faster upload

---

## Error Responses

### 400 Bad Request - Missing admin_id or student_id

**Request:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=salom"
```

**Response:**
```json
{
  "error": "admin_id yoki student_id ni jo'natish majburiy"
}
```

---

### 400 Bad Request - Both admin_id and student_id provided

**Request:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440002"
```

**Response:**
```json
{
  "error": "Faqat admin_id yoki student_id ni jo'natish mumkin, ikkalasini emas"
}
```

---

### 400 Bad Request - File too large

**Request:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -F "file=@/path/to/huge_file.zip"  # > 50MB
```

**Response:**
```json
{
  "file": ["Fayl hajmi 50MB dan oshmasligi kerak"]
}
```

---

### 400 Bad Request - Invalid file format

**Request:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -F "file=@/path/to/script.exe"
```

**Response:**
```json
{
  "file": ["Ruxsat etilgan formatlar: .pdf, .png, .jpg, .jpeg, .docx, .xlsx"]
}
```

---

### 400 Bad Request - User not found

**Request:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=salom" \
  -F "admin_id=00000000-0000-0000-0000-000000000000"
```

**Response:**
```json
{
  "admin_id": ["Admin topilmadi"]
}
```

---

### 401 Unauthorized - Missing token

**Request:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

**Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 401 Unauthorized - Invalid token

**Request:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer INVALID_TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

**Response:**
```json
{
  "detail": "Given token not valid for any token type"
}
```

---

## Complete Testing Workflow

### Step 1: Get Access Token

```bash
curl -X POST "http://91.210.106.114:8000/api/users/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_phone": "student_username",
    "password": "student_password"
  }'
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "username": "student_username",
    ...
  }
}
```

Copy the `access` token.

### Step 2: Send Message

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

### Step 3: Retrieve Messages

```bash
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## Using Python Requests

```python
import requests

# Configuration
BASE_URL = "http://91.210.106.114:8000/api"
ACCESS_TOKEN = "your_access_token_here"
ADMIN_ID = "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"

# Headers
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# Test 1: Send text-only message
data = {
    "text": "salom",
    "admin_id": ADMIN_ID
}

response = requests.post(
    f"{BASE_URL}/message/",
    headers=headers,
    data=data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Send message with file
files = {
    "file": open("/path/to/document.pdf", "rb")
}

data = {
    "text": "Mana fayl bilan xabar",
    "admin_id": ADMIN_ID
}

response = requests.post(
    f"{BASE_URL}/message/",
    headers=headers,
    data=data,
    files=files
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 3: Retrieve messages
response = requests.get(
    f"{BASE_URL}/message/?admin_id={ADMIN_ID}",
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Messages: {response.json()}")
```

---

## Using JavaScript/Fetch

```javascript
// Configuration
const BASE_URL = "http://91.210.106.114:8000/api";
const ACCESS_TOKEN = "your_access_token_here";
const ADMIN_ID = "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c";

// Test 1: Send text-only message
async function sendTextMessage() {
  const formData = new FormData();
  formData.append("text", "salom");
  formData.append("admin_id", ADMIN_ID);

  const response = await fetch(`${BASE_URL}/message/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${ACCESS_TOKEN}`
    },
    body: formData
  });

  const data = await response.json();
  console.log("Status:", response.status);
  console.log("Response:", data);
}

// Test 2: Send message with file
async function sendMessageWithFile(file) {
  const formData = new FormData();
  formData.append("text", "Mana fayl bilan xabar");
  formData.append("admin_id", ADMIN_ID);
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/message/`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${ACCESS_TOKEN}`
    },
    body: formData
  });

  const data = await response.json();
  console.log("Status:", response.status);
  console.log("Response:", data);
}

// Test 3: Retrieve messages
async function getMessages() {
  const response = await fetch(
    `${BASE_URL}/message/?admin_id=${ADMIN_ID}`,
    {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${ACCESS_TOKEN}`
      }
    }
  );

  const data = await response.json();
  console.log("Status:", response.status);
  console.log("Messages:", data);
}

// Usage
sendTextMessage();
// sendMessageWithFile(fileInput.files[0]);
// getMessages();
```

---

## Postman Collection

You can import this into Postman:

```json
{
  "info": {
    "name": "ITCLUB Messages API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Send Text Message",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "text",
              "value": "salom",
              "type": "text"
            },
            {
              "key": "admin_id",
              "value": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
              "type": "text"
            }
          ]
        },
        "url": {
          "raw": "http://91.210.106.114:8000/api/message/",
          "protocol": "http",
          "host": ["91", "210", "106", "114"],
          "port": "8000",
          "path": ["api", "message", ""]
        }
      }
    },
    {
      "name": "Send Message with File",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "text",
              "value": "Mana fayl bilan xabar",
              "type": "text"
            },
            {
              "key": "admin_id",
              "value": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
              "type": "text"
            },
            {
              "key": "file",
              "type": "file",
              "src": []
            }
          ]
        },
        "url": {
          "raw": "http://91.210.106.114:8000/api/message/",
          "protocol": "http",
          "host": ["91", "210", "106", "114"],
          "port": "8000",
          "path": ["api", "message", ""]
        }
      }
    },
    {
      "name": "Get Messages",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{access_token}}"
          }
        ],
        "url": {
          "raw": "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
          "protocol": "http",
          "host": ["91", "210", "106", "114"],
          "port": "8000",
          "path": ["api", "message", ""],
          "query": [
            {
              "key": "admin_id",
              "value": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
            }
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "access_token",
      "value": ""
    }
  ]
}
```

---

## Troubleshooting

### Issue: "Content-Type: application/json" with form data
**Problem:** Using JSON content type with form data
**Solution:** Use `multipart/form-data` (automatic with cURL -F flag)

### Issue: File not uploading
**Problem:** File path incorrect or file doesn't exist
**Solution:** Use absolute path: `/home/user/documents/file.pdf`

### Issue: 401 Unauthorized
**Problem:** Token expired or invalid
**Solution:** Get a new token from login endpoint

### Issue: 400 Bad Request
**Problem:** Missing required fields
**Solution:** Ensure both `text` and either `admin_id` or `student_id` are provided

---

## Summary

| Scenario | Method | Endpoint | Body |
|----------|--------|----------|------|
| Send text message | POST | `/api/message/` | text, admin_id/student_id |
| Send with file | POST | `/api/message/` | text, admin_id/student_id, file |
| Get messages | GET | `/api/message/?admin_id=...` | - |
| Get messages | GET | `/api/message/?student_id=...` | - |

---

**Last Updated:** November 17, 2025
