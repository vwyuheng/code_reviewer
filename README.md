# code_reviewer

# 这是一个基于大模型的coder review项目
## 依赖大模型会员，欢迎交流


## 执行安装命令
pip3 install -e .


# 显示帮助信息
python cli.py --help

# 输入被审查项目（code review project path）
python cli.py /path/to/java/project

# 默认输出到当前./reviews

# 指定输出目录和配置文件
python cli.py /path/to/java/project --output-dir ./my-reviews