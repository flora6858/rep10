import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Путь к файлу избранных пользователей
FAVORITES_FILE = "favorites.json"

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("600x500")

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        # Интерфейс
        self.create_widgets()

    def create_widgets(self):
        # Поле поиска
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(search_frame, text="Поиск пользователя GitHub:").pack(side="left")
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_user).pack(side="left")

        # Результаты поиска
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска")
        results_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.results_tree = ttk.Treeview(results_frame, columns=("Login", "Name", "Public Repos"), show="headings", height=10)
        self.results_tree.heading("Login", text="Логин")
        self.results_tree.heading("Name", text="Имя")
        self.results_tree.heading("Public Repos", text="Публичных репозиториев")
        self.results_tree.column("Login", width=150)
        self.results_tree.column("Name", width=200)
        self.results_tree.column("Public Repos", width=120)
        self.results_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки управления избранным
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=5, padx=20, fill="x")

        ttk.Button(buttons_frame, text="Добавить в избранное", command=self.add_to_favorites).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Удалить из избранного", command=self.remove_from_favorites).pack(side="left", padx=5)

        # Список избранных
        favorites_frame = ttk.LabelFrame(self.root, text="Избранные пользователи")
        favorites_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.favorites_tree = ttk.Treeview(favorites_frame, columns=("Login", "Name"), show="headings", height=5)
        self.favorites_tree.heading("Login", text="Логин")
        self.favorites_tree.heading("Name", text="Имя")
        self.favorites_tree.column("Login", width=250)
        self.favorites_tree.column("Name", width=300)
        self.favorites_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.update_favorites_display()

    def search_user(self):
        username = self.search_entry.get().strip()
        if not username:
            messagebox.showerror("Ошибка", "Поле поиска не должно быть пустым!")
            return

        try:
            response = requests.get(f"https://api.github.com/users/{username}")
            if response.status_code == 200:
                user_data = response.json()
                self.display_user_results([user_data])
            else:
                messagebox.showerror("Ошибка", f"Пользователь не найден (код: {response.status_code})")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при запросе к API: {e}")

    def display_user_results(self, users):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for user in users:
            self.results_tree.insert("", "end", values=(
                user.get("login", "N/A"),
                user.get("name", "N/A"),
                user.get("public_repos", 0)
            ))

    def add_to_favorites(self):
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из результатов поиска!")
            return

        user_data = self.results_tree.item(selected[0])["values"]
        login = user_data[0]

        if login not in self.favorites:
            self.favorites[login] = {
                "name": user_data[1],
                "public_repos": user_data[2]
            }
            self.save_favorites()
            self.update_favorites_display()
            messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное!")

    def remove_from_favorites(self):
        selected = self.favorites_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите пользователя из списка избранного!")
            return

        login = self.favorites_tree.item(selected[0])["values"][0]
        if login in self.favorites:
            del self.favorites[login]
            self.save_favorites()
            self.update_favorites_display()
            messagebox.showinfo("Успех", f"Пользователь {login} удалён из избранного!")

    def load_favorites(self):
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def update_favorites_display(self):
        for item in self.favorites_tree.get_children():
            self.favorites_tree.delete(item)

        for login, data in self.favorites.items():
            self.favorites_tree.insert("", "end", values=(login, data["name"]))

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
