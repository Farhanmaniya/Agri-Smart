from setuptools import setup, find_packages

setup(
    name="agrismart",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "tensorflow",
        "joblib",
        "pydantic",
        "scikit-learn",
        "opencv-python",
        "numpy",
        "pandas"
    ]
)