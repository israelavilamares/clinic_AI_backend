import bcrypt

def hash_passwords(password:str)->str:
    salt = bcrypt.gensalt()  # Generate a salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash the password
    return hashed.decode('utf-8')  # Convert to string for storage

output = hash_passwords("123")

print(output)