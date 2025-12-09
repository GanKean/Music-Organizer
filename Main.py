import tkinter as tk
from tkinter import ttk, messagebox

from db import (
    init_db,
    get_all_songs,
    search_songs,
    add_song,
    update_song,
    delete_song,
    get_all_playlists,
    create_playlist,
    delete_playlist,
    get_songs_for_playlist,
    add_song_to_playlist,
    remove_song_from_playlist,
)


class LibraryTab(tk.Frame):
    """Library tab: shows all songs, search, and add/edit/delete form."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.songs = []          # list of (id, title, artist, album, genre, year)
        self.selected_song_id = None

        self._build_search_area()
        self._build_song_list()
        self._build_form()

        self.refresh_songs()

    # ---------- UI builders ----------

    def _build_search_area(self):
        frame = tk.LabelFrame(self, text="Search")
        frame.pack(fill="x", padx=10, pady=5)

        tk.Label(frame, text="Keyword:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_entry = tk.Entry(frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Field:").grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.search_field = tk.StringVar(value="title")
        field_menu = ttk.Combobox(
            frame,
            textvariable=self.search_field,
            values=["title", "genre", "both"],
            width=8,
            state="readonly",
        )
        field_menu.grid(row=0, column=3, padx=5, pady=5)

        btn_search = tk.Button(frame, text="Search", command=self.search_songs)
        btn_search.grid(row=0, column=4, padx=5, pady=5)

        btn_show_all = tk.Button(frame, text="Show All", command=self.refresh_songs)
        btn_show_all.grid(row=0, column=5, padx=5, pady=5)

    def _build_song_list(self):
        frame = tk.LabelFrame(self, text="Songs")
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # scrollbar + listbox
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

        # Labels
        tk.Label(frame, text="Title:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        tk.Label(frame, text="Artist:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        tk.Label(frame, text="Album:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        tk.Label(frame, text="Genre:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        tk.Label(frame, text="Year:").grid(row=4, column=0, sticky="e", padx=5, pady=2)

        # Entries
        self.entry_title = tk.Entry(frame, width=35)
        self.entry_artist = tk.Entry(frame, width=35)
        self.entry_album = tk.Entry(frame, width=35)
        self.entry_genre = tk.Entry(frame, width=35)
        self.entry_year = tk.Entry(frame, width=10)

        self.entry_title.grid(row=0, column=1, padx=5, pady=2)
        self.entry_artist.grid(row=1, column=1, padx=5, pady=2)
        self.entry_album.grid(row=2, column=1, padx=5, pady=2)
        self.entry_genre.grid(row=3, column=1, padx=5, pady=2)
        self.entry_year.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=0, column=2, rowspan=5, padx=10, pady=2, sticky="ns")

        btn_add = tk.Button(btn_frame, text="Add Song", width=16, command=self.add_song)
        btn_update = tk.Button(btn_frame, text="Update Song", width=16, command=self.update_song)
        btn_delete = tk.Button(btn_frame, text="Delete Song", width=16, command=self.delete_song)
        btn_clear = tk.Button(btn_frame, text="Clear Form", width=16, command=self.clear_form)

        btn_add.pack(pady=2)
        btn_update.pack(pady=2)
        btn_delete.pack(pady=2)
        btn_clear.pack(pady=10)

    # ---------- Helpers ----------

    def clear_form(self):
        self.selected_song_id = None
        for entry in (
            self.entry_title,
            self.entry_artist,
            self.entry_album,
            self.entry_genre,
            self.entry_year,
        ):
            entry.delete(0, tk.END)

    def populate_listbox(self, songs):
        self.songs = songs
        self.song_listbox.delete(0, tk.END)
        for song in songs:
            song_id, title, artist, album, genre, year = song
            display = f"{title} — {artist} [{genre}] ({year})"
            self.song_listbox.insert(tk.END, display)

    def refresh_songs(self):
        try:
            songs = get_all_songs()
            self.populate_listbox(songs)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load songs:\n{e}")

    def search_songs(self):
        keyword = self.search_entry.get().strip()
        field = self.search_field.get()
        if not keyword:
            self.refresh_songs()
            return
        try:
            songs = search_songs(keyword, field)
            self.populate_listbox(songs)
        except Exception as e:
            messagebox.showerror("Error", f"Search failed:\n{e}")

    def on_song_select(self, event):
        try:
            index = self.song_listbox.curselection()[0]
        except IndexError:
            return
        song = self.songs[index]
        song_id, title, artist, album, genre, year = song
        self.selected_song_id = song_id

        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, title)

        self.entry_artist.delete(0, tk.END)
        self.entry_artist.insert(0, artist)

        self.entry_album.delete(0, tk.END)
        self.entry_album.insert(0, album)

        self.entry_genre.delete(0, tk.END)
        self.entry_genre.insert(0, genre)

        self.entry_year.delete(0, tk.END)
        self.entry_year.insert(0, str(year))

    # ---------- CRUD actions ----------

    def add_song(self):
        title = self.entry_title.get().strip()
        artist = self.entry_artist.get().strip()
        album = self.entry_album.get().strip()
        genre = self.entry_genre.get().strip()
        year = self.entry_year.get().strip()

        if not title or not artist:
            messagebox.showwarning("Validation", "Title and artist are required.")
            return

        try:
            if year:
                int(year)
        except ValueError:
            messagebox.showwarning("Validation", "Year must be a number.")
            return

        try:
            add_song(title, artist, album, genre, year)
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
        album = self.entry_album.get().strip()
        genre = self.entry_genre.get().strip()
        year = self.entry_year.get().strip()

        if not title or not artist:
            messagebox.showwarning("Validation", "Title and artist are required.")
            return

        try:
            if year:
                int(year)
        except ValueError:
            messagebox.showwarning("Validation", "Year must be a number.")
            return

        try:
            update_song(self.selected_song_id, title, artist, album, genre, year)
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

    # ---------- Access for other tabs ----------

    def get_selected_song_id(self):
        return self.selected_song_id

    def get_selected_song_display(self):
        try:
            index = self.song_listbox.curselection()[0]
        except IndexError:
            return None
        return self.song_listbox.get(index)


class PlaylistsTab(tk.Frame):
    """Playlists tab: manage playlists and their songs."""

    def __init__(self, master, library_tab: LibraryTab, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.library_tab = library_tab

        self.playlists = []           # list of (id, name)
        self.selected_playlist_id = None
        self.playlist_songs = []      # songs for selected playlist

        self._build_layout()
        self.refresh_playlists()

    def _build_layout(self):
        # Left: playlists list + controls
        left_frame = tk.LabelFrame(self, text="Playlists")
        left_frame.pack(side="left", fill="y", padx=10, pady=5)

        scrollbar_pl = tk.Scrollbar(left_frame)
        scrollbar_pl.pack(side="right", fill="y")

        self.playlist_listbox = tk.Listbox(left_frame, height=12)
        self.playlist_listbox.pack(side="left", fill="y")
        self.playlist_listbox.config(yscrollcommand=scrollbar_pl.set)
        scrollbar_pl.config(command=self.playlist_listbox.yview)

        self.playlist_listbox.bind("<<ListboxSelect>>", self.on_playlist_select)

        # Add/delete playlist controls
        ctrl_frame = tk.Frame(left_frame)
        ctrl_frame.pack(fill="x", pady=5)

        tk.Label(ctrl_frame, text="New Playlist:").pack(anchor="w", padx=5)
        self.entry_playlist_name = tk.Entry(ctrl_frame, width=20)
        self.entry_playlist_name.pack(anchor="w", padx=5, pady=2)

        btn_add_pl = tk.Button(ctrl_frame, text="Create Playlist", command=self.create_playlist)
        btn_del_pl = tk.Button(ctrl_frame, text="Delete Playlist", command=self.delete_playlist)
        btn_add_pl.pack(anchor="w", padx=5, pady=2)
        btn_del_pl.pack(anchor="w", padx=5, pady=2)

        # Right: songs in playlist + controls
        right_frame = tk.LabelFrame(self, text="Songs in Selected Playlist")
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        scrollbar_ps = tk.Scrollbar(right_frame)
        scrollbar_ps.pack(side="right", fill="y")

        self.playlist_song_listbox = tk.Listbox(right_frame, height=12)
        self.playlist_song_listbox.pack(side="left", fill="both", expand=True)
        self.playlist_song_listbox.config(yscrollcommand=scrollbar_ps.set)
        scrollbar_ps.config(command=self.playlist_song_listbox.yview)

        # Buttons under playlist songs
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

    # ---------- Playlist helpers ----------

    def populate_playlists(self, playlists):
        self.playlists = playlists
        self.playlist_listbox.delete(0, tk.END)
        for pl_id, name in playlists:
            self.playlist_listbox.insert(tk.END, name)

    def refresh_playlists(self):
        try:
            playlists = get_all_playlists()
            self.populate_playlists(playlists)
            self.selected_playlist_id = None
            self.playlist_song_listbox.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlists:\n{e}")

    def on_playlist_select(self, event):
        try:
            index = self.playlist_listbox.curselection()[0]
        except IndexError:
            return
        pl_id, name = self.playlists[index]
        self.selected_playlist_id = pl_id
        self.refresh_playlist_songs()

    def refresh_playlist_songs(self):
        if self.selected_playlist_id is None:
            self.playlist_song_listbox.delete(0, tk.END)
            return
        try:
            songs = get_songs_for_playlist(self.selected_playlist_id)
            self.playlist_songs = songs
            self.playlist_song_listbox.delete(0, tk.END)
            for song in songs:
                song_id, title, artist, album, genre, year = song
                display = f"{title} — {artist} [{genre}] ({year})"
                self.playlist_song_listbox.insert(tk.END, display)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load playlist songs:\n{e}")

    # ---------- Playlist actions ----------

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
        song_id = song[0]

        if not messagebox.askyesno("Confirm", "Remove this song from the playlist?"):
            return

        try:
            remove_song_from_playlist(self.selected_playlist_id, song_id)
            self.refresh_playlist_songs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove song from playlist:\n{e}")


class MusicOrganizerApp:
    """Main application window with tabs."""

    def __init__(self, root):
        self.root = root
        self.root.title("Music Organizer")

        # Notebook (tabs)
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.library_tab = LibraryTab(notebook)
        self.playlists_tab = PlaylistsTab(notebook, self.library_tab)

        notebook.add(self.library_tab, text="Library")
        notebook.add(self.playlists_tab, text="Playlists")


def main():
    # Initialize database (create tables, etc.)
    init_db()

    root = tk.Tk()
    app = MusicOrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
