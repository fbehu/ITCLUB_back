# Messages API - Quick Reference

## Endpoints

### 1. Get Messages
```
GET /api/message/?admin_id={admin_uuid}
GET /api/message/?student_id={student_uuid}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:** Array of messages

---

### 2. Send Message
```
POST /api/message/
```

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body (Student → Admin):**
```
text: "Message content"
admin_id: "admin-uuid"
file: [optional file]
```

**Body (Admin → Student):**
```
text: "Message content"
student_id: "student-uuid"
file: [optional file]
```

**Response:** Created message object (201)

---

## Message Object Structure

```json
{
  "id": "uuid",
  "text": "Message content",
  "admin_id": "uuid or null",
  "student_id": "uuid or null",
  "sender_name": "First Last",
  "created_at": "2025-11-16T20:30:00Z",
  "file_url": "http://example.com/media/messages/file.pdf or null",
  "file_name": "file.pdf or null"
}
```

---

## File Requirements

**Allowed Formats:**
- `.pdf`
- `.png`
- `.jpg`, `.jpeg`
- `.docx`
- `.xlsx`

**Size Limit:** 50MB

---

## Logic

- If `admin_id` is null → message sent by student
- If `student_id` is null → message sent by admin
- `sender_name` always shows who sent the message
- `created_at` is in ISO 8601 format (UTC)

---

## Error Codes

| Code | Meaning |
|------|---------|
| 201 | Message created successfully |
| 400 | Validation error (missing fields, invalid file, etc.) |
| 401 | Unauthorized (missing/invalid token) |
| 404 | User not found |

---

## Common Errors

### Missing admin_id or student_id
```json
{
  "error": "admin_id yoki student_id ni jo'natish majburiy"
}
```

### File too large
```json
{
  "file": ["Fayl hajmi 50MB dan oshmasligi kerak"]
}
```

### Invalid file format
```json
{
  "file": ["Ruxsat etilgan formatlar: .pdf, .png, .jpg, .jpeg, .docx, .xlsx"]
}
```

### User not found
```json
{
  "admin_id": ["Admin topilmadi"]
}
```

---

## Example cURL Commands

### Get messages from admin
```bash
curl -X GET "http://localhost:8000/api/message/?admin_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Send message to admin
```bash
curl -X POST "http://localhost:8000/api/message/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "text=Hello admin" \
  -F "admin_id=550e8400-e29b-41d4-a716-446655440000"
```

### Send message with file
```bash
curl -X POST "http://localhost:8000/api/message/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "text=Here is a document" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440001" \
  -F "file=@/path/to/document.pdf"
```

---

## Implementation Details

**App:** `apps/chat`
**Models:** `Message`
**Serializers:** `MessageSerializer`, `MessageCreateSerializer`
**Views:** `MessageListView`, `MessageCreateView`
**URL Prefix:** `/api/message/`

**Database:** PostgreSQL
**Authentication:** JWT (Bearer token)
**File Storage:** `media/messages/`

---

## Notes

- All timestamps are in UTC (ISO 8601 format)
- File URLs are absolute (include domain)
- Messages are ordered by creation date (newest first)
- Both admin and student can retrieve the same conversation
- Sender information is always included in responses
