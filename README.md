# GreatKart E-commerce Platform

A full-featured e-commerce platform built with Django, featuring user authentication, product management, shopping cart functionality, and order processing.

## Features

- User Authentication and Authorization
- Product Catalog with Categories
- Shopping Cart Management
- Order Processing
- Product Reviews and Ratings
- User Profile Management
- Email Verification
- Responsive Design

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository

```bash
git clone <repository-url>
cd ecommerce
```

2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages

```bash
pip install -r requirements.txt
```

4. Create a .env file in the root directory with the following variables:

```
SECRET_KEY=your_secret_key
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
```

5. Run migrations

```bash
python manage.py migrate
```

6. Create a superuser

```bash
python manage.py createsuperuser
```

7. Run the development server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
ecommerce/
├── accounts/          # User authentication and profiles
├── Cart/             # Shopping cart functionality
├── category/         # Product categories
├── greatkart/        # Main project settings
├── media/           # User-uploaded files
├── orders/          # Order processing
├── static/          # Static files (CSS, JS, images)
├── store/           # Product management
└── templates/       # HTML templates
```

## Key Features Implementation

### User Authentication

- Custom user model with email authentication
- Email verification for new accounts
- Password reset functionality

### Product Management

- Product categories and subcategories
- Product variations (size, color)
- Product image gallery
- Product reviews and ratings

### Shopping Cart

- Add/remove products
- Update quantities
- Save for later functionality

### Order Processing

- Checkout process
- Order status tracking
- Order history

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

The project follows PEP 8 style guide. To check your code:

```bash
pylint **/*.py
```

### Making Migrations

After modifying models:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django documentation
- Bootstrap for the frontend framework
- Font Awesome for icons
