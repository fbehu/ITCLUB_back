# Attendance Application

## Overview
The Attendance application is designed to manage and track attendance for various groups. It allows users to submit attendance records based on group ID and date, and provides functionality to retrieve attendance status for specific groups.

## Features
- **Group Management**: Define and manage groups for attendance tracking.
- **Attendance Records**: Record attendance status for each group on specific dates.
- **API Endpoints**: Access attendance data through RESTful API endpoints.

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd attendance
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage
1. Run the migrations to set up the database:
   ```
   python manage.py migrate
   ```
2. Start the development server:
   ```
   python manage.py runserver
   ```
3. Access the API at `http://127.0.0.1:8000/attendance/`.

## API Endpoints
- **GET /attendance/groups/{group_id}/date/{date}/**: Retrieve attendance status for a specific group on a given date.
- **POST /attendance/groups/{group_id}/attendance/**: Submit attendance for a specific group.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.