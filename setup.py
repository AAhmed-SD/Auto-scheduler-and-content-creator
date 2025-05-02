from setuptools import setup, find_packages

setup(
    name="auto-scheduler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=1.4.0,<2.0.0",
        "psycopg2-binary>=2.9.0,<3.0.0",
        "python-dotenv>=0.19.0,<1.0.0",
        "pydantic>=1.8.0,<2.0.0",
        "fastapi>=0.68.0,<1.0.0",
        "uvicorn>=0.15.0,<1.0.0",
        "python-jose[cryptography]>=3.3.0,<4.0.0",
        "passlib[bcrypt]>=1.7.4,<2.0.0",
        "python-multipart>=0.0.5,<1.0.0",
        "requests>=2.26.0,<3.0.0",
        "redis>=4.0.0,<5.0.0",
        "celery>=5.1.0,<6.0.0",
        "twilio>=7.0.0,<8.0.0",
        "boto3>=1.18.0,<2.0.0",
        "coverage>=6.0.0,<7.0.0",
    ],
    python_requires=">=3.8",
) 