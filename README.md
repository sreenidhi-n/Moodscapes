# Moodscapes 
This project is a mood-based music recommendation system developed using the Flask-MySQL framework and integrated with the Spotipy API.  

## Features
- **User Authentication**: Users can log in, register, and update their account information.
- **Mood Logging**: Users can log their mood entries, providing information on mood rating, reason, sleep quality, and exercise level.
- **Average Mood Rating**: The system calculates and displays the average mood rating for each user.
- **Music Recommendations**: Utilizing the Spotipy API, the system recommends 5 songs based on the user's latest mood rating.
- **CRUD Operations**: Basic CRUD operations are implemented for managing user credentials, mood entries, playlists, and tracks.

## Technologies Used
- **Flask**: Used for web development, providing a flexible and modular framework.
- **MySQL**: Employed for database management, storing user and mood data.
- **Spotipy API**: Integrated to fetch music recommendations based on the user's mood.

## Usage
- Log in or register to start logging your mood entries.
- Log your mood with details like rating, reason, sleep quality, and exercise level.
- Explore your mood journal to view past entries and see the average mood rating.
- Get personalized music recommendations based on your latest mood entry.
- Manage your account, including updating account information and deleting your account.

## Pre-requisites
- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-Migrate
- Spotipy
- MySQL
- A spotify developer account to retrieve your client_id, client_secret and redirect_url

## How to run the virtual environment? 
1. Clone the repository:
    ```
    git clone https://github.com/sreenidhi-n/Moodscapes.git
    cd Moodscapes
    ```
2. Set up the virtual environment
    ```
    python -m venv venv
    venv\Scripts\activate
    ```
3. Install the dependencies or pre-requisites listed above
4. Configure MySQL database
5. Run the migration
    ```
      flask db init
      flask db migrate -m "Initial migration"
      flask db upgrade
    ```
6. Run the application
    ```
      python app.py
    ```
7. Access the application at [localhost](http://localhost:5000)http://localhost:5000
