from setuptools import setup, find_packages

setup(
    name="your-project-name",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Add project metadata
    author="Your Name",
    author_email="your.email@example.com",
    description="A short description of your project",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    
    # Project dependencies
    install_requires=[
        # List your project dependencies here
        # e.g., "numpy>=1.20.0",
        # "pandas>=1.3.0",
    ],
    
    # Development dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    
    # Python version requirement
    python_requires=">=3.7",
)
