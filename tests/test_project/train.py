import torch
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def main():
    print("正在加载数据...")
    # 模拟数据加载
    X = torch.randn(1000, 10)
    y = torch.randint(0, 2, (1000,))
    
    print("数据预处理...")
    # 转换为numpy进行预处理
    X_np = X.numpy()
    y_np = y.numpy()
    
    # 数据分割
    X_train, X_test, y_train, y_test = train_test_split(
        X_np, y_np, test_size=0.2, random_state=42
    )
    
    # 标准化
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    print("环境测试完成！所有依赖都已正确安装。")

if __name__ == "__main__":
    main() 