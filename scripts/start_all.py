#!/usr/bin/env python3
"""
PassAgent 一键启动脚本 - 跨平台版本
支持 Windows、macOS、Linux
"""

import os
import sys
import subprocess
import time
import platform
import signal
import shutil
from pathlib import Path


class PassAgentLauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.processes = []

    def find_command(self, command):
        """查找命令的完整路径"""
        # 在Windows上，npm可能是npm.cmd
        if platform.system() == "Windows":
            variants = [f"{command}.cmd", f"{command}.exe", command]
        else:
            variants = [command]

        for variant in variants:
            path = shutil.which(variant)
            if path:
                return path
        return None

    def check_dependencies(self):
        """检查依赖是否安装"""
        print("🔍 检查依赖...")

        # 检查Python
        python_cmd = self.find_command("python")
        if not python_cmd:
            # 尝试python3
            python_cmd = self.find_command("python3")

        if python_cmd:
            try:
                result = subprocess.run(
                    [python_cmd, "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ Python: {result.stdout.strip()}")
                    self.python_cmd = python_cmd
                else:
                    raise FileNotFoundError
            except Exception:
                print("❌ 错误: Python命令执行失败")
                return False
        else:
            print("❌ 错误: 未找到Python，请先安装Python")
            print("下载地址: https://www.python.org/")
            return False

        # 检查Node.js
        node_cmd = self.find_command("node")
        if node_cmd:
            try:
                result = subprocess.run(
                    [node_cmd, "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ Node.js: {result.stdout.strip()}")
                    self.node_cmd = node_cmd
                else:
                    raise FileNotFoundError
            except Exception:
                print("❌ 错误: Node.js命令执行失败")
                return False
        else:
            print("❌ 错误: 未找到Node.js，请先安装Node.js")
            print("下载地址: https://nodejs.org/")
            return False

        # 检查npm
        npm_cmd = self.find_command("npm")
        if npm_cmd:
            try:
                result = subprocess.run(
                    [npm_cmd, "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ npm: {result.stdout.strip()}")
                    self.npm_cmd = npm_cmd
                else:
                    raise FileNotFoundError
            except Exception:
                print("❌ 错误: npm命令执行失败")
                return False
        else:
            print("❌ 错误: 未找到npm，请重新安装Node.js")
            return False

        return True

    def install_dependencies(self):
        """安装项目依赖"""
        print("\n📦 检查并安装依赖...")

        # 安装后端依赖
        if (self.backend_dir / "requirements.txt").exists():
            print("🐍 检查Python依赖...")
            try:
                # 先检查是否已安装fastapi
                result = subprocess.run(
                    [self.python_cmd, "-c", "import fastapi; print('installed')"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    print("安装Python依赖...")
                    subprocess.run(
                        [
                            self.python_cmd,
                            "-m",
                            "pip",
                            "install",
                            "-r",
                            "requirements.txt",
                        ],
                        cwd=self.backend_dir,
                        check=True,
                    )
                    print("✅ Python依赖安装完成")
                else:
                    print("✅ Python依赖已存在")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Python依赖安装失败: {e}")

        # 检查前端依赖
        if (self.frontend_dir / "package.json").exists():
            if not (self.frontend_dir / "node_modules").exists():
                print("📦 安装Node.js依赖...")
                try:
                    subprocess.run(
                        [self.npm_cmd, "install"], cwd=self.frontend_dir, check=True
                    )
                    print("✅ Node.js依赖安装完成")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️ Node.js依赖安装失败: {e}")
                    print("请手动运行: npm install")
            else:
                print("✅ Node.js依赖已存在")

    def start_backend(self):
        """启动后端服务"""
        print("\n🔧 启动后端服务...")

        if not self.backend_dir.exists():
            print("❌ 后端目录不存在")
            return None

        # 检查run.py是否存在
        run_file = self.backend_dir / "run.py"
        if not run_file.exists():
            print("❌ 找不到run.py文件")
            return None

        try:
            if platform.system() == "Windows":
                # Windows下创建新的命令行窗口
                process = subprocess.Popen(
                    [self.python_cmd, "run.py"],
                    cwd=self.backend_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            else:
                # Unix系统
                process = subprocess.Popen(
                    [self.python_cmd, "run.py"], cwd=self.backend_dir
                )

            self.processes.append(("backend", process))
            print("✅ 后端服务启动中...")
            return process

        except Exception as e:
            print(f"❌ 后端启动失败: {e}")
            return None

    def start_frontend(self):
        """启动前端服务"""
        print("\n🌐 启动前端服务...")

        if not self.frontend_dir.exists():
            print("❌ 前端目录不存在")
            return None

        # 检查package.json是否存在
        package_file = self.frontend_dir / "package.json"
        if not package_file.exists():
            print("❌ 找不到package.json文件")
            return None

        try:
            print(f"📍 使用npm命令: {self.npm_cmd}")
            print(f"📍 前端目录: {self.frontend_dir}")

            if platform.system() == "Windows":
                # Windows下创建新的命令行窗口
                process = subprocess.Popen(
                    [self.npm_cmd, "start"],
                    cwd=self.frontend_dir,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    shell=False,
                )
            else:
                # Unix系统
                process = subprocess.Popen(
                    [self.npm_cmd, "start"], cwd=self.frontend_dir
                )

            self.processes.append(("frontend", process))
            print("✅ 前端服务启动中...")
            return process

        except FileNotFoundError as e:
            print(f"❌ 找不到npm命令: {e}")
            print(f"npm路径: {self.npm_cmd}")
            print("请确认Node.js安装正确并且npm在PATH中")
            return None
        except Exception as e:
            print(f"❌ 前端启动失败: {e}")
            return None

    def setup_signal_handlers(self):
        """设置信号处理器，用于优雅关闭"""

        def signal_handler(signum, frame):
            print("\n\n🛑 收到停止信号，正在关闭服务...")
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        if platform.system() != "Windows":
            signal.signal(signal.SIGTERM, signal_handler)

    def cleanup(self):
        """清理进程"""
        for name, process in self.processes:
            if process.poll() is None:  # 进程仍在运行
                print(f"🔄 停止{name}服务...")
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"⚠️ 停止{name}服务时出错: {e}")

    def test_commands(self):
        """测试命令是否可用"""
        print("\n🧪 测试命令...")

        # 测试Python
        try:
            result = subprocess.run(
                [self.python_cmd, "--version"], capture_output=True, text=True
            )
            print(f"Python测试: {result.stdout.strip()}")
        except Exception as e:
            print(f"Python测试失败: {e}")

        # 测试npm
        try:
            result = subprocess.run(
                [self.npm_cmd, "--version"], capture_output=True, text=True
            )
            print(f"npm测试: {result.stdout.strip()}")
        except Exception as e:
            print(f"npm测试失败: {e}")

    def run(self):
        """主启动流程"""
        print("================================")
        print("    PassAgent 一键启动脚本")
        print("================================")
        print(f"📁 项目目录: {self.project_root}")
        print(f"🖥️ 操作系统: {platform.system()}")

        # 检查依赖
        if not self.check_dependencies():
            input("按回车键退出...")
            return False

        # 测试命令
        self.test_commands()

        # 安装依赖
        self.install_dependencies()

        # 设置信号处理
        self.setup_signal_handlers()

        # 启动后端
        backend_process = self.start_backend()
        if not backend_process:
            input("按回车键退出...")
            return False

        # 等待后端启动
        print("⏳ 等待后端服务启动... (5秒)")
        time.sleep(5)

        # 启动前端
        frontend_process = self.start_frontend()
        if not frontend_process:
            print("前端启动失败，但后端可能已启动")
            input("按回车键退出...")
            self.cleanup()
            return False

        print("\n✅ 启动完成！")
        print("📡 后端地址: http://localhost:8080")
        print("📖 API文档: http://localhost:8080/docs")
        print("🌐 前端地址: http://localhost:3000")
        print("\n💡 按 Ctrl+C 停止所有服务")

        try:
            # 等待用户中断或进程结束
            while True:
                time.sleep(1)
                # 检查进程是否还在运行
                if all(p.poll() is not None for _, p in self.processes):
                    print("🔄 所有服务已停止")
                    break
        except KeyboardInterrupt:
            print("\n🛑 用户中断")
        finally:
            self.cleanup()

        return True


if __name__ == "__main__":
    launcher = PassAgentLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)
