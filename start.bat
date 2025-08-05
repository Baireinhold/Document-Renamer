@echo off
chcp 65001 >nul
title 智能文档重命名工具 v2.1
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║    📚 智能文档重命名工具 v2.1 - Windows启动器               ║
echo ║                                                              ║
echo ║    🚀 自动检查环境和依赖                                     ║
echo ║    🔧 智能安装缺失组件                                       ║
echo ║    ⚙️ 一键启动完整功能                                       ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: ====== 检查Python环境 ======
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo.
    echo 💡 请安装Python 3.8或更高版本:
    echo    1. 访问 https://python.org/downloads/
    echo    2. 下载最新版Python
    echo    3. 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% 已安装

:: ====== 检查pip ======
echo.
echo 🔍 检查pip包管理器...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip未安装，正在尝试安装...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo ❌ pip安装失败
        pause
        exit /b 1
    )
    echo ✅ pip安装成功
) else (
    echo ✅ pip可用
)

:: ====== 检查requirements.txt ======
echo.
echo 📦 检查依赖文件...
if not exist "requirements.txt" (
    echo ❌ 未找到requirements.txt文件
    echo 💡 请确保requirements.txt文件存在于当前目录
    pause
    exit /b 1
)
echo ✅ requirements.txt文件存在

:: ====== 检查是否已安装核心依赖 ======
echo.
echo 🔍 检查核心依赖...
python -c "import rich, requests, dotenv, yaml, PyPDF2, pdfplumber" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  检测到缺失依赖，开始自动安装...
    goto :install_deps
) else (
    echo ✅ 核心依赖已安装
    goto :check_config
)

:install_deps
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                      📦 自动安装依赖                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: 尝试升级pip
echo 🔄 升级pip到最新版本...
python -m pip install --upgrade pip --quiet

:: 尝试多个镜像源安装依赖
echo.
echo 📥 开始安装Python依赖包...
echo 💡 如果官方源较慢，将自动尝试国内镜像源
echo.

:: 方案1: 官方源
echo 🌐 尝试官方源安装...
python -m pip install -r requirements.txt --timeout 60 >nul 2>&1
if not errorlevel 1 (
    echo ✅ 依赖安装成功 (官方源)
    goto :verify_installation
)

:: 方案2: 清华源
echo 🇨🇳 尝试清华大学镜像源...
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --timeout 60 >nul 2>&1
if not errorlevel 1 (
    echo ✅ 依赖安装成功 (清华源)
    goto :verify_installation
)

:: 方案3: 阿里源
echo 🇨🇳 尝试阿里云镜像源...
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple --timeout 60 >nul 2>&1
if not errorlevel 1 (
    echo ✅ 依赖安装成功 (阿里源)
    goto :verify_installation
)

:: 方案4: 豆瓣源
echo 🇨🇳 尝试豆瓣镜像源...
python -m pip install -r requirements.txt -i https://pypi.douban.com/simple --timeout 60 >nul 2>&1
if not errorlevel 1 (
    echo ✅ 依赖安装成功 (豆瓣源)
    goto :verify_installation
)

:: 方案5: 腾讯源
echo 🇨🇳 尝试腾讯云镜像源...
python -m pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple --timeout 60 >nul 2>&1
if not errorlevel 1 (
    echo ✅ 依赖安装成功 (腾讯源)
    goto :verify_installation
)

:: 所有方案都失败
echo.
echo ❌ 所有镜像源安装都失败了
echo.
echo 🔧 手动解决方案:
echo    1. 检查网络连接
echo    2. 手动执行: pip install -r requirements.txt
echo    3. 或尝试: pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.
echo 📝 常见依赖安装问题:
echo    - 网络连接问题: 检查防火墙和代理设置
echo    - 权限问题: 尝试以管理员身份运行
echo    - Python版本问题: 确保使用Python 3.8+
echo.
pause
exit /b 1

:verify_installation
echo.
echo 🔍 验证依赖安装...
python -c "import rich, requests, dotenv, yaml, PyPDF2, pdfplumber; print('所有核心依赖验证通过')" 2>nul
if errorlevel 1 (
    echo ❌ 依赖验证失败，可能存在版本冲突
    echo 💡 尝试重新安装: pip install -r requirements.txt --force-reinstall
    pause
    exit /b 1
)
echo ✅ 依赖验证通过

:check_config
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                      ⚙️  检查配置文件                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: ====== 检查.env配置文件 ======
echo 🔍 检查环境配置文件...
if not exist ".env" (
    echo ⚠️  未找到.env配置文件
    if exist "config\.env.template" (
        echo 📝 发现配置模板，正在创建.env文件...
        copy "config\.env.template" ".env" >nul
        echo ✅ 已从模板创建.env文件
    ) else if exist ".env.template" (
        echo 📝 发现配置模板，正在创建.env文件...
        copy ".env.template" ".env" >nul
        echo ✅ 已从模板创建.env文件
    ) else (
        echo ❌ 未找到配置模板文件
        echo 💡 请确保存在.env.template文件
        pause
        exit /b 1
    )
    
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║                      ⚠️  重要提醒                            ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo 📝 首次使用需要配置API密钥:
    echo.
    echo    1. 编辑 .env 文件
    echo    2. 选择一个AI服务并填入API密钥
    echo    3. 保存文件后重新运行此程序
    echo.
    echo 🔑 推荐的AI服务:
    echo    • DeepSeek: 性价比高，国内访问快
    echo    • OpenAI GPT: 功能最强
    echo    • Claude: 逻辑清晰
    echo    • Google Gemini: 免费额度大
    echo.
    echo 💡 配置完成后再次运行此程序即可开始使用
    echo.
    
    :: 询问是否打开配置文件
    set /p open_config="是否现在打开.env配置文件进行编辑? (y/n): "
    if /i "%open_config%"=="y" (
        echo 🔧 正在打开配置文件...
        start notepad.exe .env
        echo.
        echo 📝 请在记事本中编辑配置，完成后保存并关闭记事本
        echo 💡 然后重新运行此程序
    )
    echo.
    pause
    exit /b 0
) else (
    echo ✅ .env配置文件存在
)

:: ====== 检查项目目录结构 ======
echo.
echo 🔍 检查项目目录结构...
if not exist "src" (
    echo ❌ 未找到src目录
    pause
    exit /b 1
)
if not exist "data\input" (
    echo 📁 创建输入目录...
    mkdir "data\input" >nul 2>&1
)
if not exist "data\output" (
    echo 📁 创建输出目录...
    mkdir "data\output" >nul 2>&1
)
if not exist "data\logs" (
    echo 📁 创建日志目录...
    mkdir "data\logs" >nul 2>&1
)
echo ✅ 项目目录结构正常

:: ====== 启动主程序 ======
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                      🚀 启动主程序                           ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo 🎯 正在启动智能文档重命名工具...
echo.

:: 检查启动脚本
if exist "scripts\run.py" (
    python scripts\run.py
) else if exist "src\main.py" (
    python src\main.py
) else (
    echo ❌ 未找到主程序文件
    echo 💡 请确保存在 scripts\run.py 或 src\main.py
    pause
    exit /b 1
)

:: ====== 程序结束处理 ======
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                      🎉 程序执行完成                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: 检查是否有错误
if errorlevel 1 (
    echo ⚠️  程序执行过程中可能出现了错误
    echo.
    echo 🔧 常见问题解决:
    echo    1. API密钥配置错误 - 检查.env文件中的API_API_KEY
    echo    2. 网络连接问题 - 检查网络和代理设置
    echo    3. 文件权限问题 - 尝试以管理员身份运行
    echo    4. Python环境问题 - 重新安装Python和依赖
    echo.
    echo 📋 日志文件位置: data\logs\app.log
    echo 💡 查看日志文件可获取详细错误信息
) else (
    echo ✅ 程序正常结束
    echo.
    echo 📋 处理结果:
    echo    • 重命名的文件保存在输出目录中
    echo    • 需要OCR的文件已添加标记
    echo    • 详细日志记录在 data\logs\app.log
)

echo.
echo 💡 小贴士:
echo    • 再次运行可处理更多文件
echo    • 修改.env可调整处理参数
echo    • 查看README.md了解更多功能
echo.

pause