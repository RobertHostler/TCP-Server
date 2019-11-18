import socket
import crypt


def login(client, socket):
    password_tries = 3
    while password_tries > 0:
        client.send("Please enter your username:".encode("utf-8"))
        username_try = client.recv(1024).decode("utf-8")
        client.send("Please enter your password:".encode("utf-8"))
        password_try = client.recv(1024).decode("utf-8")

        if username_exists(username_try) and password_matches(username_try, password_try):
            return True
        else:
            client.send("Your username or password is incorrect. Try again.\n".encode("utf-8"))
            password_tries -= 1

    client.send("Maximum login attempts exceeded. You are being locked out.\n".encode("utf-8"))
    client.recv(0).decode("utf-8")
    client.send("q".encode("utf-8"))
    client.close()
    socket.close()
    quit()

def sign_up(client):
    client.send("Please create a new username:".encode("utf-8"))
    username_try = client.recv(1024).decode("utf-8")

    while username_exists(username_try):
        client.send("That username is already in use. Please choose another.".encode("utf-8"))
        username_try = client.recv(1024).decode("utf-8")
        if username_try == "q":
            client.close()
            quit()
    
    client.send("Now you may choose a password:".encode("utf-8"))
    password_try = client.recv(1024).decode("utf-8")

    while len(password_try) < 8:
        client.send("Your password must contain minimum 8 characters.".encode("utf-8"))
        password_try = client.recv(1024).decode("utf-8")

    password_hash = crypt.crypt(password_try, salt='METHOD_BLOWFISH')
    with open("credentials.txt", "a") as credentials:
        credentials.write(username_try + ":" + password_hash + "\n")
        client.send("Your account was created successfully! Returning you to the login page.\n".encode("utf-8"))

def username_exists(username):
    with open("credentials.txt", "r") as credentials:
        for line in credentials.readlines():
            components = line.split(":")
            savedusername = components[0].strip()

            if username == savedusername:
                return True
        else:
            return False

def password_matches(username, password):
    password_hash = crypt.crypt(password, salt='METHOD_BLOWFISH')
    with open("credentials.txt", "r") as credentials:
        for line in credentials.readlines():
            components = line.split(":")
            savedusername = components[0].strip()
            savedhash = components[1].strip()

            if username == savedusername:
                if password_hash == savedhash:
                    return True
        else:
            return False


def main():
    host, port = "127.0.0.1", 5000
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(1)
    client, addr = sock.accept()
    print("Connection from: " + str(addr))

    while True:
        client.send("Welcome! You may login or sign up now, or quit.\n[l/s/q]".encode("utf-8"))
        response = client.recv(1024).decode("utf-8")

        if response == "l" and login(client, sock):
            break
        elif response == "s":
            sign_up(client)
        elif response == "q":
            client.close()
            quit()

    client.send("Congratulations! You have logged in! You can now use Echo Chat with yourself!".encode("utf-8"))

    while True:
        data = client.recv(1024).decode("utf-8")
        if not data:
            break
        print("data received: ", data)
        
        data = data.upper()
        print("data sent back: ", data)
        client.send(data.encode("utf-8"))
    client.close()

if __name__ == "__main__":
    main()