from setuptools import setup, find_packages

setup(
    name="lkong-sentinel",
    version="0.1.0",
    description="龙空论坛（lkong.com）网文江湖版舆情监控与分析工具",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25",
        "openpyxl>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "lkong-sentinel=lkong_sentinel.cli:main",
        ],
    },
    python_requires=">=3.9",
)
