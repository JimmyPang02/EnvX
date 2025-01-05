"""
EnvX 命令行接口
"""

import click
import os
from pathlib import Path
from dotenv import load_dotenv
from .agent import EnvXAgent

# 加载.env文件
load_dotenv()

@click.group()
def cli():
    """EnvX - AI智能环境配置助手"""
    pass

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--api-key', envvar='OPENAI_API_KEY', help='OpenAI API密钥（可选，默认从.env文件读取）')
@click.option('--env-type', type=click.Choice(['conda', 'venv', 'docker']), 
              default='conda', help='环境类型：conda/venv/docker')
@click.option('--env-name', help='环境名称，默认使用项目名')
@click.option('--python-version', default='3.8', help='Python版本')
def configure(project_path, api_key, env_type, env_name, python_version):
    """配置项目环境"""
    try:
        agent = EnvXAgent(openai_api_key=api_key)
        agent.configure(
            project_path,
            env_type=env_type,
            env_name=env_name,
            python_version=python_version
        )
        click.echo("✨ 环境配置完成！")
    except ValueError as e:
        click.echo(f"❌ 配置失败: {str(e)}", err=True)
        if "API密钥" in str(e):
            click.echo("提示：您可以通过以下方式设置API密钥：")
            click.echo("1. 在.env文件中添加：OPENAI_API_KEY=your-key")
            click.echo("2. 设置环境变量：export OPENAI_API_KEY=your-key")
            click.echo("3. 使用命令行参数：--api-key=your-key")
        exit(1)
    except Exception as e:
        click.echo(f"❌ 配置失败: {str(e)}", err=True)
        exit(1)

if __name__ == '__main__':
    cli() 