from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

module = "minecraft_mod_manager"
package = module.replace("_", "-")

setup(
    name=package,
    version="0.0.2",
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
    install_requires=["selenium", "requests"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
)
