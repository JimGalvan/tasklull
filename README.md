# ToDo List Application

This is a ToDo List application built with Django. It allows users to create, manage, and share to-do lists and tasks.

## Features

- User authentication and registration
- Create and manage to-do lists
- Add tasks to to-do lists
- Share to-do lists with other users
- Order and sort to-do lists and tasks
- Flex items for additional task details

## Technologies Used

- Python
- Django
- JavaScript
- HTML/CSS

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/JimGalvan/todo-list-app.git
    cd todo-list-app
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Apply migrations:
    ```sh
    python manage.py migrate
    ```

5. Create a superuser:
    ```sh
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```sh
    python manage.py runserver
    ```

7. Open your browser and go to `http://127.0.0.1:8000/` to see the application.

## Usage

- Register a new user or log in with an existing account.
- Create new to-do lists and add tasks to them.
- Share to-do lists with other users by entering their username.
- Order and sort your to-do lists and tasks as needed.

## Project Structure

- `todo/`: Contains the main application code.
  - `models.py`: Defines the database models.
  - `views/`: Contains the view functions for handling requests.
  - `templates/`: Contains the HTML templates for rendering the web pages.
- `manage.py`: Django's command-line utility for administrative tasks.

## License

This project is licensed under the MIT License.
