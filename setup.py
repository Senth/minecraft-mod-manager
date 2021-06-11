from setuptools import find_packages, setup

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
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            f"{package}={module}.__main__:main",
            f"mcman={module}.__main__:main",
            f"mmm={module}.__main__:main",
        ],
    },
    install_requires=[
        "requests",
        "toml",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    setup_requires=[
        "setuptools_scm",
        "pytest-runner",
    ],
    tests_require=[
        "pytest",
        "mockito",
    ],
    python_requires=">=3.8",
)
