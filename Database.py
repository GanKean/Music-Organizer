import sqlite3
from pathlib import Path

DB_PATH = Path("music_organizer.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS songs (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                name   TEXT NOT NULL,
                artist TEXT,
                genre  TEXT
            );

            CREATE TABLE IF NOT EXISTS playlists (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS playlist_songs (
                playlist_id INTEGER NOT NULL,
                song_id     INTEGER NOT NULL,
                PRIMARY KEY (playlist_id, song_id),
                FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY (song_id)     REFERENCES songs(id)     ON DELETE CASCADE
            );
            """
        )
    conn.close()


def create_song(name: str, artist: str = "", genre: str = "") -> int:
    if not name.strip():
        raise ValueError("Song name cannot be empty.")

    conn = get_connection()
    with conn:
        cur = conn.execute(
            "INSERT INTO songs (name, artist, genre) VALUES (?, ?, ?)",
            (name.strip(), artist.strip(), genre.strip())
        )
        song_id = cur.lastrowid
    conn.close()
    return song_id


def get_all_songs() -> list[dict]:
    conn = get_connection()
    with conn:
        rows = conn.execute(
            "SELECT id, name, artist, genre FROM songs ORDER ORDER BY name COLLATE NOCASE"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_song(song_id: int, name: str, artist: str = "", genre: str = "") -> None:
    if not name.strip():
        raise ValueError("Song name cannot be empty.")

    conn = get_connection()
    with conn:
        conn.execute(
            "UPDATE songs SET name = ?, artist = ?, genre = ? WHERE id = ?",
            (name.strip(), artist.strip(), genre.strip(), song_id)
        )
    conn.close()


def delete_song(song_id: int) -> None:
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    conn.close()


def create_playlist(name: str) -> int:
    if not name.strip():
        raise ValueError("Playlist name cannot be empty.")

    conn = get_connection()
    with conn:
        cur = conn.execute(
            "INSERT INTO playlists (name) VALUES (?)",
            (name.strip(),)
        )
        pid = cur.lastrowid
    conn.close()
    return pid


def delete_playlist(playlist_id: int) -> None:
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
    conn.close()


def add_song_to_playlist(playlist_id: int, song_id: int) -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO playlist_songs (playlist_id, song_id) VALUES (?, ?)",
            (playlist_id, song_id)
        )
    conn.close()


def remove_song_from_playlist(playlist_id: int, song_id: int) -> None:
    conn = get_connection()
    with conn:
        conn.execute(
            "DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
            (playlist_id, song_id)
        )
    conn.close()


def search_songs_by_name(name_query: str) -> list[dict]:
    q = name_query.strip()
    conn = get_connection()
    with conn:
        rows = conn.execute(
            """
            SELECT id, name, artist, genre
            FROM songs
            WHERE name LIKE '%' || ? || '%'
            ORDER BY name COLLATE NOCASE
            """,
            (q,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_songs_by_genre(genre_query: str) -> list[dict]:
    q = genre_query.strip()
    conn = get_connection()
    with conn:
        rows = conn.execute(
            """
            SELECT id, name, artist, genre
            FROM songs
            WHERE genre LIKE '%' || ? || '%'
            ORDER BY name COLLATE NOCASE
            """,
            (q,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

