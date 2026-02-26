from config.settings import get_settings

settings = get_settings()
print(f"JWT_SECRET: '{settings.jwt_secret}'")
print(f"JWT_SECRET length: {len(settings.jwt_secret)}")
print(f"Mongo URI: {settings.mongo_uri}")
