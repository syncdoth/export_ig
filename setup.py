from setuptools import find_packages, setup

setup(
    name="export_ig",
    version="1.0.2",
    description="Package for processing images for Instagram upload.",
    # pylint: disable-next=consider-using-with
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    url="https://github.com/syncdoth/export_ig",
    author="Sehyun Choi",
    author_email="choisehyun98@gmail.com",
    license="Apache",
    packages=find_packages(exclude=[
        ".github",
        "imgs",
    ]),
    install_requires=[
        "Pillow",
        "joblib",
        "fire",
    ],
    entry_points={"console_scripts": ["export_ig=export_ig.export_ig:run"]},
    include_package_data=True,
    python_requires=">=3.8",
    zip_safe=False,
)
