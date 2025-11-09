import streamlit_authenticator as stauth

# Plain text passwords
passwords = ['password123', 'teacher123', 'principal123']

# Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()
print(hashed_passwords)
