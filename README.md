# HelpDesk Application

## Overview

The HelpDesk application is a web-based ticketing system designed to manage and track support requests. It is built using Flask, a lightweight web framework for Python, and integrates with Google OAuth for user authentication. The application allows users to create, view, and manage support tickets, and provides administrators with additional functionalities such as user management and ticket prioritization.

## Features

- **User Authentication**: Secure login using Google OAuth.
- **Ticket Management**: Create, view, update, and delete support tickets.
- **User Roles**: Different roles for administrators, third-party users, and regular users.
- **Email Notifications**: Automated email notifications for ticket updates.
- **Backup and Restore**: Admin-only feature to download database backups.
- **Category Management**: Create and manage ticket categories.
- **Procedures**: Create and manage procedural steps for resolving tickets.
- **Mobile Accessibility**: Limited access for mobile users.

## Project Structure

```
.
├── app/
│   ├── auth/
│   │   └── auth.py
│   ├── blueprints/
│   │   └── bps.py
│   ├── ext/
│   │   ├── db.py
│   │   └── migrate.py
│   ├── mail/
│   │   └── mail.py
│   ├── models/
│   │   ├── forms.py
│   │   ├── tables.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── flash.css
│   │   │   ├── index.css
│   │   │   ├── login.css
│   │   │   └── chamados.css
│   ├── templates/
│   │   ├── base_content.html
│   │   ├── base_list.html
│   │   ├── chamado.html
│   │   ├── chamados.html
│   │   ├── create_base.html
│   │   ├── create_cat.html
│   │   ├── create_ticket.html
│   │   ├── etapas.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── mail_template.html
│   │   ├── select_dep.html
│   │   ├── user.html
│   │   ├── users.html
│   │   └── view_user_lat.html
│   ├── ultils.py
│   ├── __init__.py
│   └── categories.json
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── README
│   ├── alembic.ini
│   └── script.py.mako
├── .vscode/
│   └── settings.json
├── .env
├── config.py
├── credentials.json
├── db.sqlite
├── docker-compose.yml
├── Dockerfile
├── estresser.py
├── nginx.conf
├── output/
│   └── db.sqlite
├── README.md
├── requirements.txt
├── run.py
├── run_docker.bat
└── teste_messages.py
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker (for containerized deployment)
- Node.js and npm (for front-end dependencies, if any)

### Local Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/helpdesk.git
    cd helpdesk
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a 

.env

 file in the root directory with the following content:
    ```
    export FLASK_APP=app:create_app
    export FLASK_ENV=development
    ```

5. **Initialize the database**:
    ```sh
    flask db upgrade
    ```

6. **Run the application**:
    ```sh
    flask run
    ```

### Docker Setup

1. **Build and run the Docker container**:
    ```sh
    docker-compose up --build
    ```

2. **Access the application**:
    Open your browser and navigate to `http://localhost:8001`.

## Usage

### User Authentication

- Navigate to the login page and authenticate using your Google account.

### Ticket Management

- **Create Ticket**: Fill out the form on the "Create Ticket" page.
- **View Tickets**: View all tickets on the "Tickets" page.
- **Update Ticket**: Click on a ticket to view and update its details.
- **Delete Ticket**: Admins can delete tickets from the ticket details page.

### User Management (Admin Only)

- **View Users**: Admins can view all users on the "Users" page.
- **Update User Roles**: Admins can promote or demote users to/from admin or third-party roles.
- **Delete User**: Admins can delete users, which also deletes all their tickets.

### Backup and Restore (Admin Only)

- **Download Backup**: Admins can download the database backup from the "Backup" page.

## Configuration

### Configuration File

The 

config.py

 file contains the configuration settings for the application, including the database URI and secret key.

### Environment Variables

- `FLASK_APP`: The entry point of the Flask application.
- `FLASK_ENV`: The environment in which the Flask app is running (development, production, etc.).

## Contributing

1. **Fork the repository**.
2. **Create a new branch**:
    ```sh
    git checkout -b feature/your-feature-name
    ```
3. **Make your changes**.
4. **Commit your changes**:
    ```sh
    git commit -m 'Add some feature'
    ```
5. **Push to the branch**:
    ```sh
    git push origin feature/your-feature-name
    ```
6. **Open a pull request**.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- Flask
- Google OAuth
- Bootstrap

For any questions or issues, please open an issue on GitHub or contact the project maintainer.