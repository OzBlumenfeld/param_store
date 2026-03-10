from app.services.encryption import EncryptionService


def test_envelope_encryption_cycle():
    master_key = "test-master-key"
    service = EncryptionService(master_key)

    secret_value = "my-secret-password-123"

    # 1. Generate DEK
    dek = service.generate_dek()

    # 2. Encrypt value with DEK
    encrypted_value = service.encrypt_value(secret_value, dek)
    assert encrypted_value != secret_value

    # 3. Encrypt DEK with Master Key
    encrypted_dek = service.encrypt_dek(dek)
    assert encrypted_dek != dek.decode()

    # 4. Decrypt DEK
    decrypted_dek = service.decrypt_dek(encrypted_dek)
    assert decrypted_dek == dek

    # 5. Decrypt Value
    decrypted_value = service.decrypt_value(encrypted_value, decrypted_dek)
    assert decrypted_value == secret_value


def test_unique_deks_different_ciphertexts():
    master_key = "test-master-key"
    service = EncryptionService(master_key)
    secret_value = "same-value"

    dek1 = service.generate_dek()
    dek2 = service.generate_dek()

    enc1 = service.encrypt_value(secret_value, dek1)
    enc2 = service.encrypt_value(secret_value, dek2)

    # Even with same value, different DEKs produce different ciphertext
    assert enc1 != enc2
