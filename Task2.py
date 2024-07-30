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
            raise ValueError("Ім'я не може бути порожнім")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):  # Ініціалізація телефону з перевіркою формату
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Номер телефону має складатися з 10 цифр")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):  # Ініціалізація дня народження з перевіркою формату
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте DD.MM.YYYY")

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
        return f"Ім'я контакту: {self.name.value}, телефони: {phones}, день народження: {birthday}"

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

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return str(e)
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Контакт не знайдено."
    record.edit_phone(old_phone, new_phone)
    return "Номер телефону оновлено."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Контакт не знайдено."
    return f"{name}: {', '.join(phone.value for phone in record.phones)}"

@input_error
def show_all(args, book: AddressBook):
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Контакт не знайдено."
    record.add_birthday(birthday)
    return "День народження додано."

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Контакт не знайдено."
    if record.birthday is None:
        return "День народження не встановлено."
    return f"День народження {name} - {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "Немає днів народжень на наступному тижні."
    result = "Ось список днів народження на наступний тиждень:\n"
    result += "\n".join(f"{name}: {date}" for birthday in upcoming_birthdays for name, date in birthday.items())
    return result

def parse_input(user_input):
    return user_input.strip().split()

def main():
    book = AddressBook()
    print("Ласкаво просимо до асистента!")
    while True:
        user_input = input("Введіть команду: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("До побачення!")
            break

        elif command == "hello":
            print("Чим можу допомогти?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Неправильна команда.")

if __name__ == "__main__":
    main()
