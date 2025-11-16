# Chat Tizimi API Dokumentatsiyasi

## 1. Adminlar ro'yxatini olish (Student uchun)

**Endpoint:** `GET /users/admins/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response format:**
```json
[
  {
    "id": "uuid-format",
    "first_name": "Ism",
    "last_name": "Familya",
    "photo": "http://example.com/media/admin_photo.png"
  },
  {
    "id": "uuid-format-2",
    "first_name": "Admin",
    "last_name": "Adminov",
    "photo": "http://example.com/media/admin2.png"
  }
]
```

**Kerakli maydonlar:**
- `id` (uuid) - Admin IDsi
- `first_name` (string) - Ismi
- `last_name` (string) - Familyasi
- `photo` (string, optional) - Rasm URLi

---

## 2. Studentlar ro'yxatini olish (Admin uchun)

**Endpoint:** `GET /users/users/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response format:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-format",
      "first_name": "Ziyoda",
      "last_name": "Khushvaqtovna",
      "photo": "http://example.com/media/user_photos/ziyoda.png",
      "direction": "Axborot texnologiyalari 25-01",
      "course": "kurs-1",
      "role": "student"
    }
  ]
}
```

**Kerakli maydonlar:**
- `results` array ichida:
  - `id` (uuid) - Student IDsi
  - `first_name` (string) - Ismi
  - `last_name` (string) - Familyasi
  - `photo` (string, optional) - Rasm URLi
  - `direction` (string, optional) - Yo'nalishi
  - `course` (string, optional) - Kursi
  - `role` (string) - "student" bo'lishi kerak

---

## 3. Xabarlarni olish

### Student tomonidan (admindan xabarlar)

**Endpoint:** `GET /message/?admin_id={admin_uuid}`

### Admin tomonidan (studentdan xabarlar)

**Endpoint:** `GET /message/?student_id={student_uuid}`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response format:**
```json
[
  {
    "id": "uuid-format",
    "text": "Salom, qalaysiz?",
    "admin_id": "admin-uuid",
    "student_id": null,
    "sender_name": "Admin Adminov",
    "created_at": "2025-11-16T20:30:00Z",
    "file_url": null,
    "file_name": null
  },
  {
    "id": "uuid-format-2",
    "text": "Yaxshi rahmat",
    "admin_id": null,
    "student_id": "student-uuid",
    "sender_name": "Ziyoda Khushvaqtovna",
    "created_at": "2025-11-16T20:31:00Z",
    "file_url": "http://example.com/media/files/document.pdf",
    "file_name": "document.pdf"
  }
]
```

**Kerakli maydonlar:**
- `id` (uuid) - Xabar IDsi
- `text` (string) - Xabar matni
- `admin_id` (uuid, nullable) - Agar admin yuborgan bo'lsa, admin ID. Aks holda null
- `student_id` (uuid, nullable) - Agar student yuborgan bo'lsa, student ID. Aks holda null
- `sender_name` (string, optional) - Yuboruvchi ismi
- `created_at` (datetime) - Yaratilgan vaqti (ISO 8601 format)
- `file_url` (string, nullable) - Fayl URLi (agar fayl yuborilgan bo'lsa)
- `file_name` (string, nullable) - Fayl nomi (agar fayl yuborilgan bo'lsa)

**Mantiq:**
- Agar `admin_id` null bo'lsa - student yuborgan
- Agar `student_id` null bo'lsa - admin yuborgan

---

## 4. Xabar yuborish

**Endpoint:** `POST /message/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

### Student tomonidan adminiga xabar

**Request body (FormData):**
```
text: "Xabar matni"
admin_id: "admin-uuid"
file: [File object] (optional)
```

### Admin tomonidan studentga xabar

**Request body (FormData):**
```
text: "Xabar matni"
student_id: "student-uuid"
file: [File object] (optional)
```

**Fayl talablari:**
- Maksimal hajm: 50MB
- Ruxsat etilgan formatlar: `.pdf`, `.png`, `.jpg`, `.jpeg`, `.docx`, `.xlsx`

**Success Response:** `201 Created`
```json
{
  "id": "uuid-format",
  "text": "Xabar matni",
  "admin_id": "admin-uuid",
  "student_id": null,
  "created_at": "2025-11-16T20:35:00Z",
  "file_url": "http://example.com/media/files/uploaded.pdf",
  "file_name": "uploaded.pdf"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": "Fayl hajmi 50MB dan oshmasligi kerak"
}
```

---

## Xavfsizlik

- Barcha so'rovlarda `Authorization: Bearer {access_token}` header majburiy
- 401 status code kelsa, frontend avtomatik logout qiladi va login sahifasiga yo'naltiradi
- Fayllar serverda tekshirilishi kerak (hajm, format, virus)

---

## Real-time yangilanish

Frontend har 3 sekundda `/message/` endpointga so'rov yuboradi yangi xabarlarni olish uchun. Agar WebSocket yoki real-time texnologiya qo'shsangiz, yanada yaxshi bo'ladi.
