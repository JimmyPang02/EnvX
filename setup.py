from setuptools import setup, find_packages

# 读取README作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # 包的基本信息
    name="envx",
    version="0.1.0",
    description="AI智能环境配置助手",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # 作者信息
    author="Your Name",
    author_email="your.email@example.com",
    
    # 项目主页
    url="https://github.com/yourusername/envx",
    
    # 包信息
    packages=find_packages(),  # 自动发现所有包
    include_package_data=True,  # 包含非Python文件
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 依赖包
    install_requires=[
        "openai>=1.3.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    
    # 开发依赖
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",  # 代码格式化
            "isort>=5.0.0",   # import排序
            "flake8>=4.0.0",  # 代码检查
        ],
    },
    
    # 命令行工具配置
    entry_points={
        "console_scripts": [
            "envx=envx.cli:cli",  # 安装后可以直接使用envx命令
        ],
    },
    
    # 包的分类信息
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    
    # 关键字
    keywords="environment, configuration, AI, automation",
) 