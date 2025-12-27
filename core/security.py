from passlib.context import CryptContext


CRIPTO = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(password: str, password_hash: str):
    '''
    Function to verify if the password is correct by comparing the plain text password 
    provided by the user with the password hash saved in the database during account creation.
    '''
    return CRIPTO.verify(password, password_hash)


def generate_password_hash(password: str) -> str:
    '''
    Function to generate and retunr the password hash.
    '''
    return CRIPTO.hash(password)

