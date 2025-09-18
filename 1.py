with open("demofile.txt", "a") as f:
    get_user_input = input("write: ")
    f.write(get_user_input + "\n")
