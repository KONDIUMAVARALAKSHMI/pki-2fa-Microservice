from app.crypto_utils import generate_rsa_keypair
priv_pem, pub_pem = generate_rsa_keypair()

with open('student_private.pem', 'wb') as f:
    f.write(priv_pem)

with open('student_public.pem', 'wb') as f:
    f.write(pub_pem)

print("Keys generated successfully!")
