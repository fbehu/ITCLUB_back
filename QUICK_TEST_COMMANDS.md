# Quick Test Commands - Message API

## Get Your Access Token First

```bash
curl -X POST "http://91.210.106.114:8000/api/users/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username_or_phone": "your_username_or_phone",
    "password": "your_password"
  }'
```

Copy the `access` token from the response.

---

## Test 1: Send Text-Only Message

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

**Expected Response:**
```json
{
  "id": "...",
  "text": "salom",
  "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
  "student_id": null,
  "created_at": "2025-11-17T...",
  "file_url": null,
  "file_name": null
}
```

---

## Test 2: Send Message with File

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "text=Mana fayl bilan xabar" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -F "file=@/path/to/document.pdf"
```

**Replace `/path/to/document.pdf` with your actual file path**

**Expected Response:**
```json
{
  "id": "...",
  "text": "Mana fayl bilan xabar",
  "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
  "student_id": null,
  "created_at": "2025-11-17T...",
  "file_url": "http://91.210.106.114:8000/media/messages/document.pdf",
  "file_name": "document.pdf"
}
```

---

## Test 3: Retrieve Messages

```bash
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
[
  {
    "id": "...",
    "text": "salom",
    "admin_id": "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c",
    "student_id": null,
    "sender_name": "Student Name",
    "created_at": "2025-11-17T...",
    "file_url": null,
    "file_name": null
  }
]
```

---

## Admin Sending to Student

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -F "text=Salom talaba" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440002"
```

---

## Admin Sending with File

```bash
curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -F "text=Mana topshiriq" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440002" \
  -F "file=@/path/to/assignment.pdf"
```

---

## Supported File Formats

- `.pdf` - PDF documents
- `.png` - PNG images
- `.jpg`, `.jpeg` - JPEG images
- `.docx` - Word documents
- `.xlsx` - Excel spreadsheets

**Max size:** 50MB

---

## Common Errors & Fixes

### Error: "admin_id yoki student_id ni jo'natish majburiy"
**Fix:** You must provide either `admin_id` or `student_id`

### Error: "Fayl hajmi 50MB dan oshmasligi kerak"
**Fix:** Your file is too large. Max is 50MB

### Error: "Ruxsat etilgan formatlar: .pdf, .png, .jpg, .jpeg, .docx, .xlsx"
**Fix:** Your file format is not supported

### Error: "Admin topilmadi"
**Fix:** The admin_id doesn't exist or is invalid

### Error: "Authentication credentials were not provided"
**Fix:** You forgot the Authorization header

---

## Using Postman

1. **Create new request**
2. **Method:** POST
3. **URL:** `http://91.210.106.114:8000/api/message/`
4. **Headers:**
   - `Authorization: Bearer YOUR_ACCESS_TOKEN`
5. **Body:** Form-data
   - `text` = "salom"
   - `admin_id` = "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
   - `file` = [select file] (optional)
6. **Send**

---

## Using Python

```python
import requests

token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# Send text message
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

# Send with file
files = {"file": open("document.pdf", "rb")}
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

---

## Using JavaScript

```javascript
const token = "YOUR_ACCESS_TOKEN";

// Send text message
const formData = new FormData();
formData.append("text", "salom");
formData.append("admin_id", "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c");

fetch("http://91.210.106.114:8000/api/message/", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`
  },
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));

// Send with file
const formData2 = new FormData();
formData2.append("text", "Mana fayl bilan xabar");
formData2.append("admin_id", "dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c");
formData2.append("file", fileInput.files[0]);

fetch("http://91.210.106.114:8000/api/message/", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${token}`
  },
  body: formData2
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Step-by-Step Example

### 1. Login and get token
```bash
curl -X POST "http://91.210.106.114:8000/api/users/login/" \
  -H "Content-Type: application/json" \
  -d '{"username_or_phone": "student1", "password": "pass123"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "...",
  "user": {...}
}
```

### 2. Copy the access token and use it
```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X POST "http://91.210.106.114:8000/api/message/" \
  -H "Authorization: Bearer $TOKEN" \
  -F "text=salom" \
  -F "admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c"
```

### 3. Check messages
```bash
curl -X GET "http://91.210.106.114:8000/api/message/?admin_id=dce3fc5e-c4a0-4758-8b2b-7874b1bbc97c" \
  -H "Authorization: Bearer $TOKEN"
```

---

**Last Updated:** November 17, 2025
