import setuptools

setuptools.setup(
    name="websuckets",
    version="0.0.1dev",
    author="Athropyne",
    author_email="anarchia.rulit@gmail.com",
    description="Надстройка над websockets для упрощения разработки приложений реального времени",
    url="https://github.com/athropyne/websuckets",
    packages=setuptools.find_packages(),
    install_requires=[
        "websockets",
        "pydantic"
    ]

)