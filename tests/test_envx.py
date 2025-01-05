import os
import pytest
from pathlib import Path
from envx import EnvXAgent

@pytest.fixture
def test_project_path():
    """返回测试项目路径"""
    current_dir = Path(__file__).parent
    return str(current_dir / "test_project")

@pytest.fixture
def agent():
    """创建EnvX Agent实例"""
    return EnvXAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

def test_project_analysis(agent, test_project_path):
    """测试项目分析功能"""
    requirements = agent.analyze_project(test_project_path)
    
    # 验证分析结果
    assert isinstance(requirements, dict)
    assert "python_version" in requirements
    assert "dependencies" in requirements
    
    # 验证依赖项
    deps = requirements["dependencies"]
    required_packages = {"torch", "pandas", "scikit-learn", "numpy"}
    assert all(pkg in deps for pkg in required_packages)

def test_environment_configuration(agent, test_project_path):
    """测试环境配置功能"""
    # 配置环境
    success = agent.configure(test_project_path)
    assert success
    
    # 验证环境配置
    try:
        import torch
        import pandas
        import sklearn
        import numpy
    except ImportError as e:
        pytest.fail(f"环境配置失败: {str(e)}")
        
    # 尝试运行测试项目
    test_script = Path(test_project_path) / "train.py"
    assert test_script.exists()
    
    # 执行测试脚本
    result = os.system(f"python {str(test_script)}")
    assert result == 0, "测试脚本执行失败" 