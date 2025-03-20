from setuptools import find_packages, setup

setup(
    name="cloudflare_exporter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "cloudflare==4.0.0",
        "prometheus-client==0.21.1",
        "python-dotenv==1.0.1",
        "python-json-logger==3.2.1",
        "requests==2.32.3",
        "pydantic==2.10.6",
        "pydantic-settings==2.8.1",
    ],
)
