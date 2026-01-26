#!/usr/bin/env python3
"""
Generate a secure SECRET_KEY for Flask application
"""
import secrets

if __name__ == "__main__":
    secret_key = secrets.token_hex(32)
    print("\n" + "="*60)
    print("Generated SECRET_KEY:")
    print("="*60)
    print(secret_key)
    print("="*60)
    print("\nAdd this to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print("\nOr add as environment variable in Render:")
    print(f"SECRET_KEY = {secret_key}")
    print("\n")
