from setuptools import setup, find_packages

setup(
    name="ecoflow-backend",
    version="0.1.0",
    description="Backend API for EcoFlow Waste Management & Recycling Hub",
    author="EcoFlow Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "sqlalchemy>=2.0.36",
        "psycopg2-binary>=2.9.10",
        "alembic>=1.14.0",
        "pydantic>=2.9.2",
        "pydantic-settings>=2.6.1",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.17",
        "python-dotenv>=1.0.1",
        "httpx>=0.27.2",
        "boto3>=1.35.63",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.3",
            "pytest-asyncio>=0.24.0",
            "pytest-cov>=6.0.0",
            "black>=24.10.0",
            "flake8>=7.1.1",
        ],
    },
)