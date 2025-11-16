# Message API Testing - Complete Summary

## Overview

The Message API allows students and admins to communicate by sending:
- **Text-only messages**
- **Messages with file attachments**

---

## API Endpoint

```
POST /api/message/
```

---

## Request Format

### Content-Type
```
multipart/form-data
```

### Headers
```
Authorization: Bearer {access_token}
```

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| text | string | Yes | Message content |
| admin_id | UUID | Conditional | Admin recipient (if student sending) |
| student_id | UUID | Conditional | Student recipient (if admin sending) |
| file | file | No | Optional file attachment |

**Note:** Either `admin_id` OR `student_id` must be provided, not both.

---

## Examples

### Example 1: Student Sending Text to Admin

**cURL:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

**Postman:**
- Method: POST
- URL: `http://91.210.106.114:8000/api/message/`
- Headers: `Authorization: Bearer YOUR_TOKEN`
- Body (Form-data):
  - `text` = `salom`
  - `admin_id` = `dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c`

**Python:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
data = {
    "text": "salom",
    "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
}
response = requests.post(
    "http://91.210.106.114:8000/api/message/",
    headers=headers,
    data=data
)
print(response.json())
```

**JavaScript:**
```javascript
const formData = new FormData();
formData.append("text", "salom");
formData.append("admin_id", "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c");

fetch("http://91.210.106.114:8000/api/message/", {
  method: "POST",
  headers: {
    "Authorization": "Bearer YOUR_TOKEN"
  },
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

---

### Example 2: Student Sending File to Admin

**cURL:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "text=Mana fayl bilan xabar" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -F "file=@/path/to/document.pdf"
```

**Postman:**
- Method: POST
- URL: `http://91.210.106.114:8000/api/message/`
- Headers: `Authorization: Bearer YOUR_TOKEN`
- Body (Form-data):
  - `text` = `Mana fayl bilan xabar`
  - `admin_id` = `dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c`
  - `file` = [Select file]

**Python:**
```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"file": open("/path/to/document.pdf", "rb")}
data = {
    "text": "Mana fayl bilan xabar",
    "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
}
response = requests.post(
    "http://91.210.106.114:8000/api/message/",
    headers=headers,
    data=data,
    files=files
)
print(response.json())
```

**JavaScript:**
```javascript
const formData = new FormData();
formData.append("text", "Mana fayl bilan xabar");
formData.append("admin_id", "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c");
formData.append("file", fileInput.files[0]);

fetch("http://91.210.106.114:8000/api/message/", {
  method: "POST",
  headers: {
    "Authorization": "Bearer YOUR_TOKEN"
  },
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

---

### Example 3: Admin Sending to Student

**cURL:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -F "text=Salom talaba" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440002"
```

---

### Example 4: Admin Sending File to Student

**cURL:**
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -F "text=Mana topshiriq" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440002" \
  -F "file=@/path/to/assignment.pdf"
```

---

## Response Format

### Success Response (201 Created)

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

### With File

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

## File Requirements

### Supported Formats
- `.pdf` - PDF documents
- `.png` - PNG images
- `.jpg`, `.jpeg` - JPEG images
- `.docx` - Word documents
- `.xlsx` - Excel spreadsheets

### Size Limits
- **Maximum:** 50MB
- **Recommended:** < 10MB

---

## Error Responses

### 400 Bad Request - Missing admin_id or student_id

```json
{
  "error": "admin_id yoki student_id ni jo'natish majburiy"
}
```

### 400 Bad Request - Both admin_id and student_id provided

```json
{
  "error": "Faqat admin_id yoki student_id ni jo'natish mumkin, ikkalasini emas"
}
```

### 400 Bad Request - File too large

```json
{
  "file": ["Fayl hajmi 50MB dan oshmasligi kerak"]
}
```

### 400 Bad Request - Invalid file format

```json
{
  "file": ["Ruxsat etilgan formatlar: .pdf, .png, .jpg, .jpeg, .docx, .xlsx"]
}
```

### 400 Bad Request - User not found

```json
{
  "admin_id": ["Admin topilmadi"]
}
```

or

```json
{
  "student_id": ["Student topilmadi"]
}
```

### 401 Unauthorized - Missing token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 401 Unauthorized - Invalid token

```json
{
  "detail": "Given token not valid for any token type"
}
```

---

## Step-by-Step Testing Guide

### Step 1: Get Access Token

```bash
curl -X POST "http://91.210.106.114:8000/api/users/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_phone": "your_username",
    "password": "your_password"
  }'
```

Copy the `access` token from response.

### Step 2: Send Text Message

```bash
TOKEN="your_access_token_here"

curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

### Step 3: Send Message with File

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "text=Mana fayl bilan xabar" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -F "file=@/path/to/document.pdf"
```

### Step 4: Retrieve Messages

```bash
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Testing Tools

### Option 1: cURL (Command Line)
- **Best for:** Quick testing, automation
- **Guide:** See QUICK_TEST_COMMANDS.md

### Option 2: Postman (GUI)
- **Best for:** Visual testing, team collaboration
- **Guide:** See POSTMAN_GUIDE.md

### Option 3: Python
- **Best for:** Integration testing, scripting
- **Guide:** See TEST_MESSAGE_API.md

### Option 4: JavaScript/Fetch
- **Best for:** Frontend testing, browser console
- **Guide:** See TEST_MESSAGE_API.md

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Content-Type: application/json" error | Use `multipart/form-data` instead |
| File not uploading | Check file path, size, and format |
| 401 Unauthorized | Get new token from login endpoint |
| 400 Bad Request | Ensure both text and admin_id/student_id provided |
| "Admin topilmadi" | Verify admin_id is correct and exists |
| "Fayl hajmi 50MB dan oshmasligi kerak" | File is too large, max 50MB |

---

## Documentation Files

| File | Purpose |
|------|---------|
| TEST_MESSAGE_API.md | Comprehensive testing guide |
| QUICK_TEST_COMMANDS.md | Copy-paste commands |
| POSTMAN_GUIDE.md | Postman step-by-step guide |
| MESSAGE_API_TESTING_SUMMARY.md | This file |

---

## Quick Reference

### Send Text Message
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer TOKEN" \
  -F "text=message" \
  -F "admin_id=uuid"
```

### Send with File
```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer TOKEN" \
  -F "text=message" \
  -F "admin_id=uuid" \
  -F "file=@file.pdf"
```

### Get Messages
```bash
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=uuid" \
  -H "Authorization: Bearer TOKEN"
```

---

## Next Steps

1. Choose your testing tool (cURL, Postman, Python, or JavaScript)
2. Get your access token from login endpoint
3. Test sending a text message
4. Test sending a message with file
5. Test retrieving messages
6. Verify everything works as expected

---

**Last Updated:** November 17, 2025
**Status:** Ready for testing
