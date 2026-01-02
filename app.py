from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- USERS ----------------
users = {
    "user1": {
        "name": "Chandana",
        "email": "chandana@example.com",
        "profile_pic": "images/profile.jpeg"  # include "images/" here
    }
}
current_user = "user1"

# ---------------- ARTISTS ----------------
artists = {
    "1": {"name": "Artist One", "followers": 0},
    "2": {"name": "Artist Two", "followers": 0},
    "3": {"name": "Artist Three", "followers": 0},
    "4": {"name": "Various Artists", "followers": 0}
}

# ---------------- ALBUMS ----------------
albums = {
    "1": {"name": "Melody Hits", "artist_id": "1"},
    "2": {"name": "English Pop", "artist_id": "2"},
    "3": {"name": "Trending Songs", "artist_id": "3"}
}

# ---------------- SONGS ----------------
songs = {
    "1": {"name": "Sahana Sahana", "artist_id": "1", "album_id": "1", "file": "songs/Sahana Sahana.mp3", "image": "images/Sahana Sahana.jpeg"},
    "2": {"name": "Suvvi Suvvi", "artist_id": "1", "album_id": "1", "file": "songs/Suvvi Suvvi.mp3", "image": "images/Suvvi Suvvi.jpeg"},
    "3": {"name": "The Nights", "artist_id": "2", "album_id": "2", "file": "songs/The Nights.mp3", "image": "images/The Nights.jpeg"},
    "4": {"name": "People", "artist_id": "2", "album_id": "2", "file": "songs/People.mp3", "image": "images/People.jpeg"},
    "5": {"name": "Kumkumala", "artist_id": "3", "album_id": "3", "file": "songs/Kumkumala.mp3", "image": "images/Kumkumala.jpeg"},
    "6": {"name": "Eyes Dont Lie", "artist_id": "3", "album_id": "3", "file": "songs/Eyes Dont Lie.mp3", "image": "images/Eyes Dont Lie.jpeg"},
    "7": {"name": "Barbie Girl", "artist_id": "2", "album_id": "2", "file": "songs/Barbie Girl.mp3", "image": "images/Barbie Girl.jpeg"}
}

# ---------------- PLAYLISTS ----------------
playlists = {"Liked Songs": []}  # default liked songs playlist
followed_artists = set()
liked_songs = set()
current_song = None  # Holds the currently playing song (updated only when clicking play)

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        user=users[current_user],
        songs=songs,
        albums=albums,
        artists=artists,
        liked_songs=liked_songs,
        current_song=current_song,
        playlists=playlists
    )

@app.route("/search", methods=["GET", "POST"])
def search():
    songs_result = songs
    artists_result = artists
    albums_result = albums
    if request.method == "POST":
        q = request.form.get("query", "").lower()
        songs_result = {k:v for k,v in songs.items() if q in v["name"].lower()}
        artists_result = {k:v for k,v in artists.items() if q in v["name"].lower()}
        albums_result = {k:v for k,v in albums.items() if q in v["name"].lower()}
    return render_template(
        "search.html",
        songs=songs_result,
        artists=artists_result,
        albums=albums_result,
        followed_artists=followed_artists,
        liked_songs=liked_songs,
        current_song=current_song,
        playlists=playlists
    )

@app.route("/playlists")
def show_playlists():
    return render_template(
        "playlist.html",
        playlists=playlists,
        songs=songs,
        liked_songs=liked_songs,
        current_song=current_song
    )

@app.route("/create_playlist", methods=["POST"])
def create_playlist():
    name = request.form["name"]
    if name and name not in playlists:
        playlists[name] = []
    return redirect("/playlists")

@app.route("/add_song/<playlist>/<song_id>")
def add_song(playlist, song_id):
    if playlist in playlists and song_id in songs:
        playlists[playlist].append(song_id)
    return redirect("/playlists")

@app.route("/remove_song/<playlist>/<song_id>")
def remove_song(playlist, song_id):
    if playlist in playlists and song_id in playlists[playlist]:
        playlists[playlist].remove(song_id)
    return redirect("/playlists")

@app.route("/follow/<artist_id>")
def follow(artist_id):
    followed_artists.add(artist_id)
    artists[artist_id]["followers"] += 1
    return redirect(request.referrer or "/")

@app.route("/unfollow/<artist_id>")
def unfollow(artist_id):
    if artist_id in followed_artists:
        followed_artists.remove(artist_id)
        artists[artist_id]["followers"] -= 1
    return redirect(request.referrer or "/")

@app.route("/like/<song_id>")
def like(song_id):
    if song_id in liked_songs:
        liked_songs.remove(song_id)
        if song_id in playlists["Liked Songs"]:
            playlists["Liked Songs"].remove(song_id)
    else:
        liked_songs.add(song_id)
        if song_id not in playlists["Liked Songs"]:
            playlists["Liked Songs"].append(song_id)
    return redirect(request.referrer or "/")

@app.route("/play_song/<song_id>")
def play_song(song_id):
    global current_song
    if song_id in songs:
        current_song = songs[song_id]
    return redirect(request.referrer or "/")

@app.route("/album/<album_id>")
def album_page(album_id):
    album_songs = {k:v for k,v in songs.items() if v.get("album_id") == album_id}
    album = albums[album_id]
    return render_template("album.html", album=album, songs=album_songs, liked_songs=liked_songs, current_song=current_song)

@app.route("/artist/<artist_id>")
def artist_page(artist_id):
    artist_songs = {k:v for k,v in songs.items() if v.get("artist_id") == artist_id}
    artist = artists[artist_id]
    return render_template("artist.html", artist=artist, songs=artist_songs, liked_songs=liked_songs, current_song=current_song, followed_artists=followed_artists)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    user = users[current_user]
    if request.method == "POST":
        user["name"] = request.form["name"]
        user["email"] = request.form["email"]
    return render_template(
        "profile.html",
        user=user,
        songs=songs,
        liked_songs=liked_songs,
        current_song=current_song,
        playlists=playlists
    )

@app.route("/logout")
def logout():
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
