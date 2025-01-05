"""
EnvX Agent的核心实现
"""

from typing import Dict, List, Optional
from pathlib import Path
import json
import subprocess
import sys
import os
from rich.console import Console
from rich.progress import Progress
from openai import OpenAI
from dotenv import load_dotenv


api_key="<DeepSeek API Key>"
class EnvXAgent:
    def __init__(self, openai_api_key: Optional[str] = None):
        """初始化EnvX Agent

        Args:
            openai_api_key: DeepSeek API密钥，如果为None则从环境变量或.env文件读取
        """
        # 加载.env文件
        load_dotenv()
        
        self.console = Console()
        # 优先使用传入的API密钥，其次使用环境变量
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        print(api_key)
        if not api_key:
            raise ValueError("未找到OpenAI API密钥，请在.env文件中设置OPENAI_API_KEY或通过参数传入")
            
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
    def analyze_project(self, project_path: str) -> Dict:
        """分析项目需求

        Args:
            project_path: 项目路径

        Returns:
            Dict: 项目环境需求
        """
        path = Path(project_path)
        if not path.exists():
            raise ValueError(f"项目路径 {project_path} 不存在")
            
        # 读取项目的README和依赖文件
        requirements = self._collect_requirements(path)
        
        # 使用LLM分析项目需求
        analysis = self._analyze_with_llm(requirements)
        
        return analysis
        
    def configure(self, project_path: str, env_type: str = 'conda', 
                 env_name: Optional[str] = None, python_version: str = '3.8') -> bool:
        """配置项目环境"""
        self.console.print("\n[bold blue]开始环境配置流程[/bold blue]")
        
        # 如果未指定环境名称，使用项目目录名
        if not env_name:
            env_name = Path(project_path).name
        self.console.print(f"[blue]项目路径:[/blue] {project_path}")
        self.console.print(f"[blue]环境类型:[/blue] {env_type}")
        self.console.print(f"[blue]环境名称:[/blue] {env_name}")
        self.console.print(f"[blue]Python版本:[/blue] {python_version}\n")
            
        # 1. 分析项目
        self.console.print("\n[bold yellow]步骤1: 分析项目需求[/bold yellow]")
        requirements = self.analyze_project(project_path)
        self.console.print("[green]项目需求分析结果:[/green]")
        self.console.print(json.dumps(requirements, indent=2))
        
        # 2. 规划配置步骤
        self.console.print("\n[bold yellow]步骤2: 规划配置步骤[/bold yellow]")
        steps = self._plan_configuration(requirements, env_type, env_name, python_version)
        self.console.print("[green]配置步骤规划结果:[/green]")
        self.console.print(json.dumps(steps, indent=2))
        
        # 3. 执行配置
        self.console.print("\n[bold yellow]步骤3: 执行配置[/bold yellow]")
        total_steps = len(steps)
        for i, step in enumerate(steps, 1):
            self.console.print(f"\n[blue]执行步骤 {i}/{total_steps}:[/blue]")
            self.console.print(json.dumps(step, indent=2))
            self._execute_step(step)
            self.console.print(f"[green]完成步骤 {i}/{total_steps}[/green]")
                
        self.console.print("\n[bold green]环境配置完成！[/bold green]")
        return True
        
    def _collect_requirements(self, path: Path) -> Dict:
        """收集项目需求信息"""
        requirements = {}
        
        # 读取README
        readme = path / "README.md"
        if readme.exists():
            requirements["readme"] = readme.read_text()
            
        # 读取依赖文件
        req_files = [
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "package.json"
        ]
        
        for req_file in req_files:
            req_path = path / req_file
            if req_path.exists():
                requirements[req_file] = req_path.read_text()
                
        return requirements
        
    def _analyze_with_llm(self, requirements: Dict) -> Dict:
        """使用LLM分析项目需求"""
        messages = [
            {"role": "system", "content": """你是一个专业的环境配置分析专家。
你必须严格按照JSON格式返回结果。
不要返回任何其他内容，只返回JSON。"""},
            {"role": "user", "content": f"""分析以下项目信息并提取环境配置需求。

直接返回JSON格式，不要有任何其他文字。格式如下：
{{
    "python_version": "3.8",
    "dependencies": {{
        "package_name": "version_requirement"
    }}
}}

项目信息：
{json.dumps(requirements, indent=2)}"""}
        ]
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0
        )
        
        # 添加调试信息
        print("\n=== API响应内容 ===")
        print(response.choices[0].message.content)
        print("==================\n")
        
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            self.console.print(f"[red]解析JSON失败[/red]: {str(e)}")
            self.console.print("API返回的原始内容:")
            self.console.print(response.choices[0].message.content)
            raise
        
    def _plan_configuration(self, requirements: Dict, env_type: str, 
                          env_name: str, python_version: str) -> List[Dict]:
        """规划配置步骤"""
        messages = [
            {"role": "system", "content": """你是一个专业的环境配置专家。
你必须严格按照JSON格式返回结果。
不要返回任何其他内容，只返回JSON。"""},
            {"role": "user", "content": f"""根据以下需求规划配置步骤。

直接返回JSON格式，不要有任何其他文字,一点不能有```json这类的字样。格式如下：
{{
  "steps": [
    {{
      "type": "create_conda_env",
      "params": {{
        "name": "{env_name}",
        "python_version": "{python_version}"
      }}
    }},
    {{
      "type": "install_package",
      "params": {{
        "name": "package_name",
        "version": "version_requirement",
        "method": "pip"
      }}
    }}
  ]
}}

可用的步骤类型和参数说明：
1. install_package:
   - name: 包名
   - version: 版本号（可选），保持原始格式，如">="、"=="等
   - method: 安装方法（统一使用"pip"）
2. create_venv:
   - path: 虚拟环境路径
3. create_conda_env:
   - name: 环境名
   - python_version: Python版本
4. create_dockerfile:
   - name: 镜像名
   - python_version: Python版本

注意：所有Python包都使用pip安装，包括PyTorch等。

环境类型：{env_type}
环境名称：{env_name}
Python版本：{python_version}

需求信息：
{json.dumps(requirements, indent=2)}"""}
        ]
        
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0
        )
        
        # 添加调试信息
        print("\n=== API响应内容 ===")
        print(response.choices[0].message.content)
        print("==================\n")
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get("steps", [])
        except json.JSONDecodeError as e:
            self.console.print(f"[red]解析JSON失败[/red]: {str(e)}")
            self.console.print("API返回的原始内容:")
            self.console.print(response.choices[0].message.content)
            raise

    def _execute_step(self, step: Dict):
        """执行单个配置步骤"""
        step_type = step.get("type")
        params = step.get("params", {})
        
        self.console.print(f"[yellow]执行操作:[/yellow] {step_type}")
        self.console.print(f"[yellow]参数:[/yellow] {json.dumps(params, indent=2)}")
        
        if step_type == "install_package":
            package_name = params.get("name")
            version = params.get("version")
            
            # 处理版本号格式
            if version:
                if any(op in version for op in ['>=', '<=', '==', '>', '<', '!=']):
                    package_spec = f"{package_name}{version}"
                else:
                    package_spec = f"{package_name}=={version}"
            else:
                package_spec = package_name
                
            self.console.print(f"[blue]准备安装包:[/blue] {package_spec}")
                
            try:
                if 'CONDA_PREFIX' in os.environ:
                    python_path = os.path.join(os.environ['CONDA_PREFIX'], 'bin', 'python')
                    self.console.print(f"[blue]使用Conda环境Python:[/blue] {python_path}")
                else:
                    python_path = sys.executable
                    self.console.print(f"[blue]使用系统Python:[/blue] {python_path}")
                    
                self.console.print("[yellow]执行pip安装...[/yellow]")
                subprocess.check_call([
                    python_path,
                    "-m", 
                    "pip", 
                    "install", 
                    package_spec
                ])
                self.console.print(f"[green]✓[/green] 已安装 {package_spec}")
            except subprocess.CalledProcessError as e:
                self.console.print(f"[red]✗[/red] 安装 {package_spec} 失败")
                self.console.print(f"[red]错误信息:[/red] {str(e)}")
                raise
                
        elif step_type == "create_venv":
            venv_path = params.get("path", "venv")
            try:
                subprocess.check_call([
                    sys.executable,
                    "-m",
                    "venv",
                    venv_path
                ])
                self.console.print(f"[green]✓[/green] 已创建虚拟环境: {venv_path}")
            except subprocess.CalledProcessError as e:
                self.console.print(f"[red]✗[/red] 创建虚拟环境失败: {str(e)}")
                raise
                
        elif step_type == "create_conda_env":
            env_name = params.get("name", "myenv")
            python_version = params.get("python_version", "3.8")
            
            self.console.print(f"[blue]创建Conda环境:[/blue] {env_name}")
            self.console.print(f"[blue]Python版本:[/blue] {python_version}")
            
            try:
                self.console.print("[yellow]执行conda create...[/yellow]")
                subprocess.check_call([
                    "conda",
                    "create",
                    "-y",
                    "-n",
                    env_name,
                    f"python={python_version}"
                ])
                self.console.print(f"[green]✓[/green] 已创建Conda环境: {env_name}")
                
                self.console.print("[yellow]设置环境变量...[/yellow]")
                conda_base = subprocess.check_output(["conda", "info", "--base"]).decode().strip()
                os.environ['CONDA_PREFIX'] = os.path.join(conda_base, "envs", env_name)
                self.console.print(f"[blue]CONDA_PREFIX:[/blue] {os.environ['CONDA_PREFIX']}")
                
            except subprocess.CalledProcessError as e:
                self.console.print(f"[red]✗[/red] 创建Conda环境失败")
                self.console.print(f"[red]错误信息:[/red] {str(e)}")
                raise
                
        elif step_type == "create_dockerfile":
            dockerfile_content = f"""FROM python:{params.get('python_version', '3.8')}

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
"""
            dockerfile_path = Path(params.get('path', '.')) / 'Dockerfile'
            dockerfile_path.write_text(dockerfile_content)
            self.console.print(f"[green]✓[/green] 已创建Dockerfile: {dockerfile_path}")
            
            # 如果指定了构建，则构建镜像
            if params.get('build', False):
                image_name = params.get('name', 'myapp')
                try:
                    subprocess.check_call([
                        "docker",
                        "build",
                        "-t",
                        image_name,
                        "."
                    ])
                    self.console.print(f"[green]✓[/green] 已构建Docker镜像: {image_name}")
                except subprocess.CalledProcessError as e:
                    self.console.print(f"[red]✗[/red] 构建Docker镜像失败: {str(e)}")
                    raise
        
        else:
            raise ValueError(f"未知的步骤类型: {step_type}") 