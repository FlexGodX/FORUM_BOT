import json
import os

class PersistentDict:
    def __init__(self, filename='persistent_dict.txt'):
        self.filename = filename
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                try:
                    self.data = json.load(file)
                except json.JSONDecodeError:
                    print("Ошибка при чтении файла. Создан новый словарь.")
                    self.data = {}
        else:
            self.data = {}

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.save()

    def __delitem__(self, key):
        del self.data[key]
        self.save()

    def __contains__(self, key):
        return key in self.data

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return str(self.data)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def update(self, other_dict):
        self.data.update(other_dict)
        self.save()

    def clear(self):
        self.data.clear()
        self.save()

    def update_subdict(self, main_key, sub_dict):
        """
        Обновляет подсловарь по ключу main_key.
        Если подсловарь не существует, он будет создан.
        """
        if main_key not in self.data:
            self.data[main_key] = {}

        self.data[main_key].update(sub_dict)
        self.save()
       