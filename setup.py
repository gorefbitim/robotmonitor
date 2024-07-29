from setuptools import setup, find_packages

setup(
    name="robot-monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=['python-dotenv','requests','urllib3'],
    entry_points={
        'console_scripts': [
        'robot-monitor=scripts.elasticsearch_error_notifier:main',
        ],
    },
    # Metadata
    author="Ofer Rahat",
    author_email="leofer@gmail.com",
    description="A tool to monitor and notify robot log errors.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gorefbitim/robot-monitor",
    classifiers=[
         "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
         "Operating System :: Microsoft :: Windows",
         "Operating System :: POSIX :: Linux",
    ],
)
