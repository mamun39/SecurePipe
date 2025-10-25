# Intentionally simplistic app (with some patterns scanners can catch)
import os
API_KEY = "hardcoded-secret-demo"   # Gitleaks should flag
print("Hello SecurePipe", os.getenv("ENV","dev"))