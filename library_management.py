import csv
from datetime import datetime

class Book:
    def __init__(self, book_id, title, author, genre, copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.copies = copies

class Member:
    def __init__(self, member_id, name, membership_type):
        self.member_id = member_id
        self.name = name
        self.membership_type = membership_type
        self.issued_books = []
        self.fines = 0

    def issue_book(self, book):
        if book.copies > 0:
            book.copies -= 1
            self.issued_books.append((book, datetime.now()))
            return "Book issued successfully."
        return "No copies available."

    def return_book(self, book_id):
        for book, issue_date in self.issued_books:
            if book.book_id == book_id:
                self.issued_books.remove((book, issue_date))
                book.copies += 1
                return self.calculate_fine(book_id)
        return "Book not found."

    def calculate_fine(self, book_id):
        fine_per_day = 1  # $1 per day overdue
        for book, issue_date in self.issued_books:
            if book.book_id == book_id:
                days_overdue = (datetime.now() - issue_date).days - 14  
                if days_overdue > 0:
                    self.fines += days_overdue * fine_per_day
        return self.fines

class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.users = {}
        self.load_books_from_csv()
        self.load_members_from_csv()
        self.load_users_from_csv()

    def load_books_from_csv(self):
        try:
            with open('books.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    book = Book(row['book_id'], row['title'], row['author'], row['genre'], int(row['copies']))
                    self.books[book.book_id] = book
        except FileNotFoundError:
            print("books.csv file not found.")

    def load_members_from_csv(self):
        try:
            with open('members.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    member = Member(int(row['member_id']), row['name'], row['membership_type'])
                    self.members[member.member_id] = member
        except FileNotFoundError:
            print("members.csv file not found.")

    def update_book(self, book_id, title=None, author=None, genre=None, copies=None):
        if book_id in self.books:
            book = self.books[book_id]
            if title:
                book.title = title
            if author:
                book.author = author
            if genre:
                book.genre = genre
            if copies is not None:
                book.copies = copies
            self.save_books_to_csv()  # Save the updated book information to the CSV
            return f"Book ID {book_id} has been updated."
        else:
            return "Invalid book ID."


    def load_users_from_csv(self):
        try:
            with open('users.csv', mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.users[row['username']] = row['password']
        except FileNotFoundError:
            print("users.csv file not found.")

    def save_books_to_csv(self):
        with open('books.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['book_id', 'title', 'author', 'genre', 'copies'])
            for book_id, book in self.books.items():
                writer.writerow([book.book_id, book.title, book.author, book.genre, book.copies])

    def save_members_to_csv(self):
        with open('members.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['member_id', 'name', 'membership_type'])
            for member_id, member in self.members.items():
                writer.writerow([member.member_id, member.name, member.membership_type])

    def save_users_to_csv(self):
        with open('users.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['username', 'password'])
            for username, password in self.users.items():
                writer.writerow([username, password])

    def add_book(self, book_id, title, author, genre, copies):
        book = Book(book_id, title, author, genre, copies)
        self.books[book_id] = book
        self.save_books_to_csv()
        return "Book added successfully."

    def add_member(self, member_id, name, membership_type):
        member = Member(member_id, name, membership_type)
        self.members[member_id] = member
        self.save_members_to_csv()
        return "Member added successfully."

    def issue_book(self, member_id, book_id):
        member = self.members.get(member_id)
        book = self.books.get(book_id)
        if member and book:
            result = member.issue_book(book)
            self.save_books_to_csv()
            self.save_members_to_csv()
            return result
        return "Book or member not found."

    def return_book(self, member_id, book_id):
        member = self.members.get(member_id)
        if member:
            result = member.return_book(book_id)
            self.save_books_to_csv()
            self.save_members_to_csv()
            return result
        return "Member not found."

    def pay_fine(self, member_id, amount):
        member = self.members.get(member_id)
        if member:
            member.fines -= amount
            self.save_members_to_csv()
            return f"Fine paid. Remaining fine: {member.fines}"
        return "Member not found."

    def list_available_books(self):
        available_books = [book for book in self.books.values() if book.copies > 0]
        if available_books:
            result = "\nAvailable Books:\n"
            for book in available_books:
                result += f"{book.book_id}: {book.title} by {book.author} - {book.copies} copies\n"
            return result
        else:
            return "No books available."

    def view_members(self):
        if not self.members:
            return "No members available."
    
        member_list = []
        for member_id, member in self.members.items():
            member_list.append(f"Member ID: {member_id}, Name: {member.name}, Membership Type: {member.membership_type}, Fine: {member.fines}")
    
        return "\n".join(member_list)


    
    def list_issued_books(self):
        issued_books = []
        for member in self.members.values():
            for book, issue_date in member.issued_books:
                issued_books.append((book.title, member.name, issue_date))
        return issued_books if issued_books else "No issued books."

    def overdue_books(self):
        overdue_list = []
        for member in self.members.values():
            for book, issue_date in member.issued_books:
                fine = member.calculate_fine(book.book_id)
                if fine > 0:
                    overdue_list.append((book.title, member.name, fine))
        return overdue_list if overdue_list else "No overdue books."

    def authenticate(self, username, password):
        if username in self.users and self.users[username] == password:
            return username
        return None

library = Library()

def library_menu():
    print("\nWelcome to the Library Management System")
    print("1. Admin Login")
    print("2. User Login")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        admin_menu()
    elif choice == "2":
        user_menu()
    elif choice == "3":
        print("Exiting the system. Goodbye!")
        exit()
    else:
        print("Invalid choice. Try again.")
        library_menu()

def admin_menu():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    if library.authenticate(username, password) == "admin":
        print(f"Welcome, {username} (Admin)")
        while True:
            print("\nAdmin Menu:")
            print("1. Add Book")
            print("2. Add Member")
            print("3. Update Book")
            print("4. Update Member")
            print("5. View Available Books")
            print("6. View Available members")
            print("7. View Issued Books")
            print("8. View Overdue Books")
            print("9. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                book_id = input("Enter book ID: ")
                title = input("Enter book title: ")
                author = input("Enter book author: ")
                genre = input("Enter book genre: ")
                copies = int(input("Enter number of copies: "))
                print(library.add_book(book_id, title, author, genre, copies))
            elif choice == "2":
                member_id = int(input("Enter member ID: "))
                name = input("Enter member name: ")
                membership_type = input("Enter membership type: ")
                print(library.add_member(member_id, name, membership_type))
            elif choice == "3":
                book_id = input("Enter book ID to update: ")
                title = input("Enter new title (leave blank to skip): ")
                author = input("Enter new author (leave blank to skip): ")
                genre = input("Enter new genre (leave blank to skip): ")
                copies = input("Enter new number of copies (leave blank to skip): ")
                if copies:
                    copies = int(copies)
                else:
                    copies = None
                print(library.update_book(book_id, title, author, genre, copies))
            elif choice == "4":
                member_id = int(input("Enter member ID: "))
                name = input("Enter new name (leave blank to skip): ")
                membership_type = input("Enter new membership type (leave blank to skip): ")
                print(library.update_member(member_id, name, membership_type))
            elif choice == "5":
                print("Available Books:")
                print(library.list_available_books())
            elif choice == "6":  
                print(library.view_members())
            elif choice == "7":
                print("Issued Books:")
                print(library.list_issued_books())
            elif choice == "8":
                print("Overdue Books:")
                print(library.overdue_books())
            elif choice == "9":
                library_menu()
            else:
                print("Invalid choice. Try again.")
    else:
        print("Invalid admin credentials.")
        library_menu()

def user_menu():
    username = input("Enter username: ")
    password = input("Enter password: ")

    user = library.authenticate(username, password)
    if user:
        print(f"Welcome, {username} (User)")
        while True:
            print("\nUser Menu:")
            print("1. View Available Books")
            print("2. Issue Book")
            print("3. Return Book")
            print("4. Pay Fine")
            print("5. Logout")

            choice = input("Enter your choice: ")

            if choice == "1":
                print("Available Books:")
                print(library.list_available_books())
            elif choice == "2":
                member_id = int(input("Enter your member ID: "))
                book_id = input("Enter the book ID to issue: ")
                print(library.issue_book(member_id, book_id))
            elif choice == "3":
                member_id = int(input("Enter your member ID: "))
                book_id = input("Enter the book ID to return: ")
                print(library.return_book(member_id, book_id))
            elif choice == "4":
                member_id = int(input("Enter your member ID: "))
                amount = float(input("Enter amount to pay: "))
                print(library.pay_fine(member_id, amount))
            elif choice == "5":
                library_menu()
            else:
                print("Invalid choice. Try again.")
    else:
        print("Invalid user credentials.")
        library_menu()

if __name__ == "__main__":
    library_menu()
