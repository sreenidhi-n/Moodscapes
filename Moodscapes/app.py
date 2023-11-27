from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask_migrate import Migrate
from sqlalchemy import text
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:SreenidhiN02@localhost/dbma_proj'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialising the API
sp_oauth = SpotifyOAuth(client_id='d930a40ed6114cf8ba8959078f1055a7', client_secret='501ecf3273dd4f868c1c0524279cbf6a', redirect_uri='http://127.0.0.1:5000/callback', scope='user-library-read playlist-read-private')
sp = spotipy.Spotify(auth_manager=sp_oauth)

#Creation of tables
class MoodPlaylistRelationship(db.Model):
    relationship_id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.TIMESTAMP, default=datetime.utcnow)

class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True)
    playlist_url = db.Column(db.String(255), nullable=False)
    playlist_name = db.Column(db.String(255), nullable=False)
    playlist_description = db.Column(db.String(255), nullable=False)
    spotify_playlist_id = db.Column(db.String(255), nullable=True)  # New field for Spotify playlist ID
    relationship_id = db.Column(db.Integer, db.ForeignKey('mood_playlist_relationship.relationship_id'), nullable=False)
    comprises_of = db.relationship('ComprisesOf', back_populates='playlist')

class Track(db.Model):
    track_id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(255), nullable=False)
    track_url = db.Column(db.String(255), nullable=False)
    comprises_of = db.relationship('ComprisesOf', back_populates='track')

class ComprisesOf(db.Model):
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.playlist_id'), primary_key=True, autoincrement=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.track_id'), primary_key=True)
    playlist = db.relationship('Playlist', back_populates='comprises_of')
    track = db.relationship('Track', back_populates='comprises_of')

class MoodEntry(db.Model):
    mood_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_rating = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date)
    mood_reason = db.Column(db.String(255), nullable=False)
    sleep_quality = db.Column(db.String(20), nullable=False)
    exercise_level = db.Column(db.String(20), nullable=False)
    created_on = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    relationship_id = db.Column(db.Integer, db.ForeignKey('mood_playlist_relationship.relationship_id'), nullable=False)

    def __init__(self, user_id, date, mood_rating, mood_reason, sleep_quality, exercise_level, relationship_id):
        self.user_id = user_id
        self.mood_rating = mood_rating
        self.mood_reason = mood_reason
        self.sleep_quality = sleep_quality
        self.exercise_level = exercise_level
        self.date = date
        self.relationship_id = relationship_id

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(200))
    mood_id = db.Column(db.Integer, db.ForeignKey('mood_entry.mood_id'))
    average_mood_rating = db.Column(db.Float)  # Add this field to the User class

    def check_password(self, password):
        return check_password_hash(self.password, password)

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Validating entered username
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):  # Check the hashed password
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256') # Secure password storage using SHA256

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/mood_journal')
@login_required
def mood_journal():
    mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.desc()).all()
    average_rating = get_average_mood_rating(current_user.id)

    if mood_entries:
        return render_template('mood_journal.html', mood_entries=mood_entries,average_rating=average_rating)
    else:
        flash('No mood entries found. Please log your mood first.', 'info')
        return redirect(url_for('mood_entry'))

def get_average_mood_rating(user_id):
    query = text("SELECT average_mood_rating FROM user WHERE id = :user_id")
    result = db.session.execute(query, {'user_id': user_id}).fetchone()
    if result:
        average_rating = result[0]
        return average_rating
    else:
        return None

@app.route('/mood_entry', methods=['GET', 'POST'])
@login_required
def mood_entry():
    if request.method == 'POST':
        # Mood data from the user's form entry
        mood_rating = int(request.form['mood_rating'])
        mood_reason = request.form['mood_reason']
        sleep_quality = request.form['sleep_quality']
        exercise_level = request.form['exercise_level']

        new_relationship = MoodPlaylistRelationship()
        db.session.add(new_relationship)
        db.session.commit()
        relationship_id = new_relationship.relationship_id

        # Create a new Mood Entry record
        new_mood_entry = MoodEntry(
            user_id=current_user.id,
            mood_rating=mood_rating,
            mood_reason=mood_reason,
            sleep_quality=sleep_quality,
            exercise_level=exercise_level,
            date=datetime.utcnow(),
            relationship_id=relationship_id
        )

        db.session.add(new_mood_entry)
        db.session.commit()

        current_user.mood_id = new_mood_entry.mood_id
        db.session.commit()

        flash('Mood entry recorded successfully!', 'success')
        print('success')
    return render_template('mood_entry.html')

def fetch_music_recommendations(sp, mood_rating):
    seed_genres = get_seed_genres_based_on_mood_rating(mood_rating)
    recommendations = sp.recommendations(seed_genres=seed_genres, limit=5)
    recommendations_list = []

    for track in recommendations['tracks']:
        track_name = track['name']
        artist_name = ", ".join([artist['name'] for artist in track['artists']])
        album_name = track['album']['name']
        external_url = track['external_urls']['spotify']

        recommendation = {
            'track_name': track_name,
            'artist_name': artist_name,
            'album_name': album_name,
            'external_url': external_url
        }

        recommendations_list.append(recommendation)

    return recommendations_list

def get_seed_genres_based_on_mood_rating(mood_rating):
    # Function to map mood ratings to appropriate music genres 
    if mood_rating <= 3:
        return ['acoustic','sad','piano']
    elif 3 < mood_rating <= 7:
        return ['french','rock']
    else:
        return ['upbeat', 'happy','pop']


@app.route('/music_recommendations')
@login_required
def music_recommendations():
    sp_oauth = SpotifyOAuth(
        client_id='d930a40ed6114cf8ba8959078f1055a7',
        client_secret='501ecf3273dd4f868c1c0524279cbf6a',
        redirect_uri='http://127.0.0.1:5000/callback',
        scope='user-library-read playlist-read-private' 
    )
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    # mood_entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.desc()).all()
    latest_mood_entry = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date.desc()).first()
    mood_rating = latest_mood_entry.mood_rating if latest_mood_entry else None

    if mood_rating:
        recommendations = fetch_music_recommendations(sp, mood_rating)
        return render_template('music_recommendations.html', recommendations=recommendations)
    else:
        #flash('No mood entry found for recommendations. Please log your mood first.', 'danger')
        return redirect(url_for('mood_entry'))

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    access_token = token_info['access_token']
    refresh_token = token_info['refresh_token']
    return redirect(url_for('dashboard'))

@app.route('/update_account', methods=['POST'])
@login_required
def update_account():
    if request.method == 'POST':
        new_username = request.form['new_username']
        new_password = request.form['new_password']
        current_user.username = new_username
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()

        flash('Account information updated successfully!', 'success')
        return redirect(url_for('user_profile'))

    return render_template('user_profile.html')

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        if 'delete' in request.form:
            db.session.delete(current_user)
            db.session.commit()
            logout_user()

            flash('Account deleted successfully. We hope to see you again!', 'success')
            return redirect(url_for('login'))

        flash('Account not deleted. Checkbox not selected.', 'warning')

    return render_template('user_profile.html')

trigger_avg_rating = '''
    DELIMITER //

    CREATE TRIGGER UpdateAverageMoodRating
    AFTER INSERT ON mood_entry
    FOR EACH ROW
    BEGIN
        DECLARE average_rating FLOAT;

        -- Calculate the average mood rating for the given user
        SELECT AVG(mood_rating) INTO average_rating
        FROM mood_entry
        WHERE user_id = NEW.user_id;

        -- Update the user's average mood rating in the users table
        UPDATE user
        SET average_mood_rating = average_rating
        WHERE id = NEW.user_id;
    END //

    DELIMITER ;
'''


if __name__ == '__main__':
    with db.engine.connect() as conn:
        conn.execute(trigger_avg_rating)
    app.run(debug=True)