from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="minecraft-mod-updater",
    version="0.0.1",
    url="https://github.com/Senth/minecraft-mod-updater",
    license="MIT",
    author="Matteus Magnusson",
    author_email="senth.wallace@gmail.com",
    description="Download and update Minecraft mods from CurseForge and possibly other places in the future.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["minecraft_mod_updater"],
    entry_points={
        "console_scripts": [
            "minecraft-mod-updater=minecraft_mod_updater:__main__:main",
        ],
    },
    include_package_data=True,
    data_files=[("config/minecraft-mod-updater", ["config/config.example.py"])],
    install_requires=["selenium"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
)
