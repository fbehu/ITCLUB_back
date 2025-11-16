# Messages API Implementation

## Overview
The messages API has been successfully implemented in the `apps/chat` application. This API allows admin and student users to communicate with each other through text messages and file sharing.

## Architecture

### Models
**Message Model** (`apps/chat/models.py`)
- `id` (UUID): Primary key
- `text` (TextField): Message content
- `admin` (ForeignKey): Reference to admin user (nullable)
- `student` (ForeignKey): Reference to student user (nullable)
- `sender` (ForeignKey): Reference to the user who sent the message
- `file` (FileField): Optional file attachment
- `created_at` (DateTime): Message creation timestamp
- `updated_at` (DateTime): Last update timestamp

**Logic:**
- Either `admin` or `student` field must be null (not both)
- If `admin` is null → message was sent by student
- If `student` is null → message was sent by admin
- `sender` always contains the user who sent the message

### Serializers

#### MessageSerializer (Read-only)
Used for retrieving messages. Returns:
- `id`: Message UUID
- `text`: Message content
- `admin_id`: Admin UUID (null if student sent)
- `student_id`: Student UUID (null if admin sent)
- `sender_name`: Full name of sender
- `created_at`: ISO 8601 timestamp
- `file_url`: Absolute URL to file (if exists)
- `file_name`: Original filename (if exists)

#### MessageCreateSerializer (Write-only)
Used for creating messages. Accepts:
- `text`: Message content (required)
- `admin_id`: UUID of admin recipient (required if student sending)
- `student_id`: UUID of student recipient (required if admin sending)
- `file`: File attachment (optional)

**Validations:**
- Either `admin_id` or `student_id` must be provided (not both)
- File size must not exceed 50MB
- File format must be one of: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.docx`, `.xlsx`

### Views

#### MessageListView (GET)
**Endpoint:** `GET /api/message/`

**Query Parameters:**
- `admin_id`: UUID of admin (student retrieves messages from this admin)
- `student_id`: UUID of student (admin retrieves messages from this student)

**Behavior:**
- Student provides `admin_id` to get all messages with that admin
- Admin provides `student_id` to get all messages with that student
- Returns messages ordered by creation date (newest first)
- Requires authentication

**Response:** Array of Message objects

#### MessageCreateView (POST)
**Endpoint:** `POST /api/message/`

**Request Format:** `multipart/form-data`

**Student sending to Admin:**
```
text: "Message content"
admin_id: "admin-uuid"
file: [optional file]
```

**Admin sending to Student:**
```
text: "Message content"
student_id: "student-uuid"
file: [optional file]
```

**Response:** Created Message object with status 201

**Error Responses:**
- 400: Validation error (missing fields, invalid file, etc.)
- 401: Unauthorized (missing/invalid token)

## API Endpoints

### Get Messages
```
GET /api/message/?admin_id={admin_uuid}
GET /api/message/?student_id={student_uuid}

Headers:
  Authorization: Bearer {access_token}
```

### Send Message
```
POST /api/message/

Headers:
  Authorization: Bearer {access_token}
  Content-Type: multipart/form-data

Body:
  text: "Message content"
  admin_id: "admin-uuid" OR student_id: "student-uuid"
  file: [optional]
```

## File Handling

### Supported Formats
- `.pdf` - PDF documents
- `.png` - PNG images
- `.jpg`, `.jpeg` - JPEG images
- `.docx` - Word documents
- `.xlsx` - Excel spreadsheets

### Size Limits
- Maximum file size: 50MB
- Files are stored in `media/messages/` directory

### File URLs
- Files are served with absolute URLs
- Example: `http://example.com/media/messages/document.pdf`

## Security Features

1. **Authentication Required**
   - All endpoints require valid JWT token
   - Invalid/expired tokens return 401 Unauthorized

2. **File Validation**
   - File size checked before upload
   - File extension validated against whitelist
   - Files stored in dedicated directory

3. **User Validation**
   - Admin/Student IDs validated against database
   - Users can only send to valid recipients
   - Role-based filtering (admin_id must be admin user, student_id must be student user)

## Database Indexes

For performance optimization, the following indexes are created:
- `(admin, created_at)` - For filtering messages by admin
- `(student, created_at)` - For filtering messages by student
- `(sender, created_at)` - For filtering messages by sender

## Installation & Setup

### 1. App Registration
The `apps.chat` app is registered in `config/settings.py`:
```python
INSTALLED_APPS = [
    ...
    "apps.chat",
    ...
]
```

### 2. URL Configuration
URLs are configured in `apps/common/urls.py`:
```python
path("message/", include("apps.chat.urls")),
```

### 3. Database Migrations
Migrations have been created and applied:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Example Usage

### Student retrieving messages from admin
```bash
curl -X GET "http://localhost:8000/api/message/?admin_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer {access_token}"
```

### Admin retrieving messages from student
```bash
curl -X GET "http://localhost:8000/api/message/?student_id=550e8400-e29b-41d4-a716-446655440001" \
  -H "Authorization: Bearer {access_token}"
```

### Student sending message to admin
```bash
curl -X POST "http://localhost:8000/api/message/" \
  -H "Authorization: Bearer {access_token}" \
  -F "text=Hello admin" \
  -F "admin_id=550e8400-e29b-41d4-a716-446655440000" \
  -F "file=@document.pdf"
```

### Admin sending message to student
```bash
curl -X POST "http://localhost:8000/api/message/" \
  -H "Authorization: Bearer {access_token}" \
  -F "text=Hello student" \
  -F "student_id=550e8400-e29b-41d4-a716-446655440001"
```

## Response Examples

### Get Messages Response
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "Salom, qalaysiz?",
    "admin_id": "550e8400-e29b-41d4-a716-446655440001",
    "student_id": null,
    "sender_name": "Admin Adminov",
    "created_at": "2025-11-16T20:30:00Z",
    "file_url": null,
    "file_name": null
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "text": "Yaxshi rahmat",
    "admin_id": null,
    "student_id": "550e8400-e29b-41d4-a716-446655440003",
    "sender_name": "Ziyoda Khushvaqtovna",
    "created_at": "2025-11-16T20:31:00Z",
    "file_url": "http://example.com/media/messages/document.pdf",
    "file_name": "document.pdf"
  }
]
```

### Create Message Response
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "text": "Xabar matni",
  "admin_id": "550e8400-e29b-41d4-a716-446655440001",
  "student_id": null,
  "created_at": "2025-11-16T20:35:00Z",
  "file_url": "http://example.com/media/messages/uploaded.pdf",
  "file_name": "uploaded.pdf"
}
```

## Error Handling

### Validation Errors (400)
```json
{
  "error": "admin_id yoki student_id ni jo'natish majburiy"
}
```

### File Size Error (400)
```json
{
  "file": ["Fayl hajmi 50MB dan oshmasligi kerak"]
}
```

### File Format Error (400)
```json
{
  "file": ["Ruxsat etilgan formatlar: .pdf, .png, .jpg, .jpeg, .docx, .xlsx"]
}
```

### User Not Found (400)
```json
{
  "admin_id": ["Admin topilmadi"]
}
```

### Unauthorized (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Admin Panel

The Message model is registered in Django admin at `/superadmin-cyber-topdingku/chat/message/`

Features:
- View all messages
- Filter by admin, student, or date
- Search by message content or username
- View file attachments

## Performance Considerations

1. **Database Indexes**: Queries are optimized with indexes on frequently filtered fields
2. **Pagination**: Can be added if needed for large message lists
3. **Caching**: Can be implemented for frequently accessed conversations
4. **File Storage**: Consider using cloud storage (S3, etc.) for production

## Future Enhancements

1. Message read/unread status
2. Message editing and deletion
3. Typing indicators
4. Real-time notifications (WebSocket)
5. Message search functionality
6. Conversation grouping
7. Message reactions/emojis
8. Voice/video message support
