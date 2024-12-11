import bcrypt

def hash_passwords(password:str)->str:
    salt = bcrypt.gensalt()  # Generate a salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash the password
    return hashed.decode('utf-8')  # Convert to string for storage

def verify_password(plain_password:str, hash_password:str)->bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'),hash_password.encode('utf-8'))
