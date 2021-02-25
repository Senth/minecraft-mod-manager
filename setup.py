from setuptools import setup
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

module = "minecraft_mod_manager"
package = module.replace("_", "-")

setup(
    name=package,
    use_scm_version=True,
    url="https://github.com/Senth/minecraft-mod-manager",
    license="MIT",
    author="Matteus Magnusson",
    author_email="senth.wallace@gmail.com",
    description="Download and update Minecraft mods from CurseForge and possibly other places in the future.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[f"{module}"],
    entry_points={
        "console_scripts": [
            f"{package}={module}.__main__:main",
        ],
    },
    include_package_data=True,
    data_files=[(f"config/{package}", ["config/config.example.py"])],
    install_requires=[
        "selenium",
        "requests",
        "webdriver-manager",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    setup_reqires=["setuptools_scm"],
    python_requires=">=3.8",
)
