import sqlite3
from pathlib import Path

DB_PATH = Path("music_organizer.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    sql_script = """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            artist TEXT,
            genre TEXT
        );

        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS playlist_songs (
            playlist_id INTEGER NOT NULL,
            song_id INTEGER NOT NULL,
            PRIMARY KEY (playlist_id, song_id),
            FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
            FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
        );
    """

    cur.executescript(sql_script)
    conn.commit()
    conn.close()


def create_song(name, artist="", genre=""):
    if name.strip() == "":
        raise ValueError("Song name cannot be empty.")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO songs (name, artist, genre) VALUES (?, ?, ?)",
        (name.strip(), artist.strip(), genre.strip())
    )

    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_all_songs():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, artist, genre FROM songs ORDER BY name COLLATE NOCASE"
    )
    rows = cur.fetchall()

    conn.close()
    return [dict(row) for row in rows]


def update_song(song_id, name, artist="", genre=""):
    if name.strip() == "":
        raise ValueError("Song name cannot be empty.")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE songs SET name = ?, artist = ?, genre = ? WHERE id = ?",
        (name.strip(), artist.strip(), genre.strip(), song_id)
    )

    conn.commit()
    conn.close()


def delete_song(song_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()


def create_playlist(name):
    if name.strip() == "":
        raise ValueError("Playlist name cannot be empty.")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO playlists (name) VALUES (?)",
        (name.strip(),)
    )

    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return new_id


def delete_playlist(playlist_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
    conn.commit()
    conn.close()


def add_song_to_playlist(playlist_id, song_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)",
        (playlist_id, song_id)
    )

    conn.commit()
    conn.close()


def remove_song_from_playlist(playlist_id, song_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
        (playlist_id, song_id)
    )

    conn.commit()
    conn.close()


def search_songs_by_name(name_query):
    q = name_query.strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, artist, genre
        FROM songs
        WHERE name LIKE '%' || ? || '%'
        ORDER BY name COLLATE NOCASE
        """,
        (q,)
    )

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_songs_by_genre(genre_query):
    q = genre_query.strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, artist, genre
        FROM songs
        WHERE genre LIKE '%' || ? || '%'
        ORDER BY name COLLATE NOCASE
        """,
        (q,)
    )

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

