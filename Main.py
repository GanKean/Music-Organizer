import tkinter as tk
from tkinter import ttk, messagebox

from Database import (
    init_db,
    get_connection,
    create_song,
    get_all_songs,
    update_song,
    delete_song,
    create_playlist,
    delete_playlist,
    add_song_to_playlist,
    remove_song_from_playlist,
    search_songs_by_name,
    search_songs_by_genre,
)

def fetch_all_playlists():
    """Return list of dicts: [{'id': ..., 'name': ...}, ...]."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM playlists ORDER BY name COLLATE NOCASE")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_songs_for_playlist(playlist_id):
    """Return list of dicts for the songs in a playlist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.id, s.name, s.artist, s.genre
        FROM songs s
        JOIN playlist_songs ps ON s.id = ps.song_id
        WHERE ps.playlist_id = ?
        ORDER BY s.name COLLATE NOCASE
        """,
        (playlist_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# --------------------------- LIBRARY TAB --------------------------- #

class LibraryTab(tk.Frame):
    """Library tab: shows all songs, search, and add/edit/delete form."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # list of dicts: {'id', 'name', 'artist', 'genre'}
        self.songs = []
        self.selected_song_id = None

        self._build_search_area()
        self._build_song_list()
        self._build_form()

        self.refresh_songs()

    # UI sections

    def _build_search_area(self):
        frame = tk.LabelFrame(self, text="Search")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Keyword:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_entry = tk.Entry(frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_field = tk.StringVar(value="name")
        rb_name = tk.Radiobutton(frame, text="By Name", variable=self.search_field, value="name")
        rb_genre = tk.Radiobutton(frame, text="By Genre", variable=self.search_field, value="genre")
        rb_name.grid(row=0, column=2, padx=5, pady=5)
        rb_genre.grid(row=0, column=3, padx=5, pady=5)

        btn_search = tk.Button(frame, text="Search", command=self.search_songs)
        btn_search.grid(row=0, column=4, padx=5, pady=5)

        btn_show_all = tk.Button(frame, text="Show All", command=self.refresh_songs)
        btn_show_all.grid(row=0, column=5, padx=5, pady=5)

    def _build_song_list(self):
        frame = tk.LabelFrame(self, text="Songs")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.song_listbox = tk.Listbox(frame, height=12, activestyle="none")
        self.song_listbox.pack(side="left", fill="both", expand=True)
        self.song_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.song_listbox.yview)

        self.song_listbox.bind("<<ListboxSelect>>", self.on_song_select)

    def _build_form(self):
        frame = tk.LabelFrame(self, text="Song Details")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        tk.Label(frame, text="Artist:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        tk.Label(frame, text="Genre:").grid(row=2, column=0, sticky="e", padx=5, pady=2)

        self.entry_title = tk.Entry(frame, width=35)
        self.entry_artist = tk.Entry(frame, width=35)
        self.entry_genre = tk.Entry(frame, width=35)

        self.entry_title.grid(row=0, column=1, padx=5, pady=2)
        self.entry_artist.grid(row=1, column=1, padx=5, pady=2)
        self.entry_genre.grid(row=2, column=1, padx=5, pady=2)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=0, column=2, rowspan=3, padx=10, pady=2, sticky="ns")

        btn_add = tk.Button(btn_frame, text="Add Song", width=16, command=self.add_song)
        btn_update = tk.Button(btn_frame, text="Update Song", width=16, command=self.update_song)
        btn_delete = tk.Button(btn_frame, text="Delete Song", width=16, command=self.delete_song)
        btn_clear = tk.Button(btn_frame, text="Clear Form", width=16, command=self.clear_form)

        btn_add.pack(pady=2)
        btn_update.pack(pady=2)
        btn_delete.pack(pady=2)
        btn_clear.pack(pady=10)

    # Helpers

    def clear_form(self):
        self.selected_song_id = None
        self.entry_title.delete(0, tk.END)
        self.entry_artist.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)

    def populate_listbox(self, songs):
        self.songs = songs
        self.song_listbox.delete(0, tk.END)
        for song in songs:
            display = f"{song['name']} — {song['artist']} [{song['genre']}]"
            self.song_listbox.insert(tk.END, display)

    def refresh_songs(self):
        try:
            songs = get_all_songs()  # list of dicts from Database.py
            self.populate_listbox(songs)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load songs:\n{e}")

    def search_songs(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_songs()
            return
        try:
            if self.search_field.get() == "name":
                songs = search_songs_by_name(keyword)
            else:
                songs = search_songs_by_genre(keyword)
            self.populate_listbox(songs)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed:\n{e}")

    def on_song_select(self, event):
        try:
            index = self.song_listbox.curselection()[0]
        except IndexError:
            return
        song = self.songs[index]  # dict
        self.selected_song_id = song["id"]

        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, song["name"])

        self.entry_artist.delete(0, tk.END)
        self.entry_artist.insert(0, song["artist"])

        self.entry_genre.delete(0, tk.END)
        self.entry_genre.insert(0, song["genre"])

    # CRUD actions

    def add_song(self):
        title = self.entry_title.get().strip()
        artist = self.entry_artist.get().strip()
        genre = self.entry_genre.get().strip()

        if not title:
            messagebox.showwarning("Validation", "Title is required.")
            return

        try:
            create_song(title, artist, genre)
            self.refresh_songs()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add song:\n{e}")

    def update_song(self):
        if self.selected_song_id is None:
            messagebox.showinfo("Select Song", "Please select a song to update.")
            return

        title = self.entry_title.get().strip()
        artist = self.entry_artist.get().strip()
        genre = self.entry_genre.get().strip()

        if not title:
            messagebox.showwarning("Validation", "Title is required.")
            return

        try:
            update_song(self.selected_song_id, title, artist, genre)
            self.refresh_songs()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update song:\n{e}")

    def delete_song(self):
        if self.selected_song_id is None:
            messagebox.showinfo("Select Song", "Please select a song to delete.")
            return

        if not messagebox.askyesno("Confirm", "Delete this song?"):
            return

        try:
            delete_song(self.selected_song_id)
            self.refresh_songs()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete song:\n{e}")

    # For playlists tab

    def get_selected_song_id(self):
        return self.selected_song_id


# -------------------------- PLAYLISTS TAB -------------------------- #

class PlaylistsTab(tk.Frame):
    """Playlists tab: manage playlists and their songs."""

    def __init__(self, master, library_tab: LibraryTab, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.library_tab = library_tab

        # list of dicts: {'id', 'name'}
        self.playlists = []
        self.selected_playlist_id = None

        # list of dicts: {'id', 'name', 'artist', 'genre'}
        self.playlist_songs = []

        self._build_layout()
        self.refresh_playlists()

    def _build_layout(self):
        # left side: playlists
        left_frame = tk.LabelFrame(self, text="Playlists")
        left_frame.pack(side="left", fill="y", padx=10, pady=5)

        scrollbar_pl = tk.Scrollbar(left_frame)
        scrollbar_pl.pack(side="right", fill="y")

        self.playlist_listbox = tk.Listbox(left_frame, height=12)
        self.playlist_listbox.pack(side="left", fill="y")
        self.playlist_listbox.config(yscrollcommand=scrollbar_pl.set)
        scrollbar_pl.config(command=self.playlist_listbox.yview)

        self.playlist_listbox.bind("<<ListboxSelect>>", self.on_playlist_select)

        ctrl_frame = tk.Frame(left_frame)
        ctrl_frame.pack(fill="x", pady=5)

        tk.Label(ctrl_frame, text="New Playlist:").pack(anchor="w", padx=5)
        self.entry_playlist_name = tk.Entry(ctrl_frame, width=20)
        self.entry_playlist_name.pack(anchor="w", padx=5, pady=2)

        btn_add_pl = tk.Button(ctrl_frame, text="Create Playlist", command=self.create_playlist)
        btn_del_pl = tk.Button(ctrl_frame, text="Delete Playlist", command=self.delete_playlist)
        btn_add_pl.pack(anchor="w", padx=5, pady=2)
        btn_del_pl.pack(anchor="w", padx=5, pady=2)

        # right side: songs in playlist
        right_frame = tk.LabelFrame(self, text="Songs in Selected Playlist")
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        scrollbar_ps = tk.Scrollbar(right_frame)
        scrollbar_ps.pack(side="right", fill="y")

        self.playlist_song_listbox = tk.Listbox(right_frame, height=12)
        self.playlist_song_listbox.pack(side="left", fill="both", expand=True)
        self.playlist_song_listbox.config(yscrollcommand=scrollbar_ps.set)
        scrollbar_ps.config(command=self.playlist_song_listbox.yview)

        # buttons under playlist songs
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)

        btn_add_song_to_pl = tk.Button(
            btn_frame,
            text="Add Selected Library Song to Playlist",
            command=self.add_selected_library_song_to_playlist,
        )
        btn_remove_song_from_pl = tk.Button(
            btn_frame,
            text="Remove Selected Song from Playlist",
            command=self.remove_selected_song_from_playlist,
        )

        btn_add_song_to_pl.pack(side="left", padx=5)
        btn_remove_song_from_pl.pack(side="left", padx=5)

    # playlist helpers

    def refresh_playlists(self):
        try:
            self.playlists = fetch_all_playlists()
            self.playlist_listbox.delete(0, tk.END)
            for pl in self.playlists:
                self.playlist_listbox.insert(tk.END, pl["name"])
            self.selected_playlist_id = None
            self.playlist_song_listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlists:\n{e}")

    def on_playlist_select(self, event):
        try:
            index = self.playlist_listbox.curselection()[0]
        except IndexError:
            return
        pl = self.playlists[index]
        self.selected_playlist_id = pl["id"]
        self.refresh_playlist_songs()

    def refresh_playlist_songs(self):
        if self.selected_playlist_id is None:
            self.playlist_song_listbox.delete(0, tk.END)
            return
        try:
            self.playlist_songs = fetch_songs_for_playlist(self.selected_playlist_id)
            self.playlist_song_listbox.delete(0, tk.END)
            for song in self.playlist_songs:
                display = f"{song['name']} — {song['artist']} [{song['genre']}]"
                self.playlist_song_listbox.insert(tk.END, display)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlist songs:\n{e}")

    # playlist actions

    def create_playlist(self):
        name = self.entry_playlist_name.get().strip()
        if not name:
            messagebox.showwarning("Validation", "Playlist name cannot be empty.")
            return
        try:
            create_playlist(name)
            self.entry_playlist_name.delete(0, tk.END)
            self.refresh_playlists()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create playlist:\n{e}")

    def delete_playlist(self):
        if self.selected_playlist_id is None:
            messagebox.showinfo("Select Playlist", "Please select a playlist to delete.")
            return

        if not messagebox.askyesno("Confirm", "Delete this playlist and its song links?"):
            return

        try:
            delete_playlist(self.selected_playlist_id)
            self.refresh_playlists()
            self.playlist_song_listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete playlist:\n{e}")

    def add_selected_library_song_to_playlist(self):
        if self.selected_playlist_id is None:
            messagebox.showinfo("Select Playlist", "Select a playlist first.")
            return

        song_id = self.library_tab.get_selected_song_id()
        if song_id is None:
            messagebox.showinfo("Select Song", "Select a song from the Library tab.")
            return

        try:
            add_song_to_playlist(self.selected_playlist_id, song_id)
            self.refresh_playlist_songs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add song to playlist:\n{e}")

    def remove_selected_song_from_playlist(self):
        if self.selected_playlist_id is None:
            messagebox.showinfo("Select Playlist", "Select a playlist first.")
            return

        try:
            index = self.playlist_song_listbox.curselection()[0]
        except IndexError:
            messagebox.showinfo("Select Song", "Select a song from the playlist list.")
            return

        song = self.playlist_songs[index]
        song_id = song["id"]

        if not messagebox.askyesno("Confirm", "Remove this song from the playlist?"):
            return

        try:
            remove_song_from_playlist(self.selected_playlist_id, song_id)
            self.refresh_playlist_songs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove song from playlist:\n{e}")


# ---------------------------- MAIN APP ---------------------------- #

class MusicOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Organizer")

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.library_tab = LibraryTab(notebook)
        self.playlists_tab = PlaylistsTab(notebook, self.library_tab)

        notebook.add(self.library_tab, text="Library")
        notebook.add(self.playlists_tab, text="Playlists")


def main():
    init_db()
    root = tk.Tk()
    app = MusicOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
