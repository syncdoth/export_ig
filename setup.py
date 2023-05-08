from setuptools import find_packages, setup

setup(
    name="export_ig",
    version="1.0.1",
    description="Package for processing images for Instagram upload.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    url="https://instagram.com/synch.poto",
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