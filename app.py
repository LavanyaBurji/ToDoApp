from auth import register, login, logout

current_user = None

while True:

    print("\n===== TODO APP =====")
    print("1. Register")
    print("2. Login")
    print("3. Logout")
    print("4. Exit")

    choice = input("Choose: ")

    if choice == "1":
        register()

    elif choice == "2":
        current_user = login()

        if current_user:
            print(f"Welcome {current_user['username']}!")

    elif choice == "3":
        current_user = logout()

    elif choice == "4":
        print("Goodbye!")
        break

    else:
        print("Invalid option.")