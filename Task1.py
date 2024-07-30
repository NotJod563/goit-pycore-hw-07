from datetime import datetime, timedelta
from collections import UserDict
import re

class Field:
    def __init__(self, value):  # Ініціалізація поля
        self.value = value

    def __str__(self):  # Представлення поля у вигляді рядка
        return str(self.value)

class Name(Field):
    def __init__(self, value):  # Ініціалізація імені
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):  # Ініціалізація телефону з перевіркою формату
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):  # Ініціалізація дня народження з перевіркою формату
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):  # Ініціалізація запису з ім'ям
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):  # Додавання телефону до запису
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):  # Видалення телефону з запису
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):  # Редагування телефону в записі
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone

    def find_phone(self, phone):  # Пошук телефону в записі
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):  # Додавання дня народження до запису
        self.birthday = Birthday(birthday)

    def __str__(self):  # Представлення запису у вигляді рядка
        phones = '; '.join(p.value for p in self.phones)
        birthday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):  # Додавання запису до адресної книги
        self.data[record.name.value] = record

    def find(self, name):  # Пошук запису за ім'ям
        return self.data.get(name, None)

    def delete(self, name):  # Видалення запису за ім'ям
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):  # Отримання списку днів народжень на наступному тижні
        today = datetime.today().date()
        next_week = today + timedelta(days=7)
        last_week = today - timedelta(days=7)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if today <= birthday_this_year < next_week:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()) % 7)
                    upcoming_birthdays.append({record.name.value: birthday_this_year.strftime("%d.%m.%Y")})
                elif last_week < birthday_this_year <= today and birthday_this_year.weekday() >= 5:
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()) % 7)
                    upcoming_birthdays.append({record.name.value: birthday_this_year.strftime("%d.%m.%Y")})

        return upcoming_birthdays

# Приклад використання

book = AddressBook()

john_record = Record("John")
john_record.add_phone("1234567890")
john_record.add_phone("5555555555")
john_record.add_birthday("4.08.1990")
book.add_record(john_record)

jane_record = Record("Jane")
jane_record.add_phone("9876543210")
jane_record.add_birthday("31.07.1985")
book.add_record(jane_record)

for name, record in book.data.items():
    print(record)

john = book.find("John")
john.edit_phone("1234567890", "1112223333")
print(john)

found_phone = john.find_phone("5555555555")
print(f"{john.name}: {found_phone}")

book.delete("Jane")

upcoming_birthdays_list = book.get_upcoming_birthdays()
print("Список привітань на цьому тижні:", upcoming_birthdays_list)
