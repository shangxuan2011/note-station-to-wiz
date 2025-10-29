import os
import subprocess
import argparse
import sys
from pathlib import Path


class MarkdownConverter:
    def __init__(self, pandoc_path="pandoc.exe"):
        self.pandoc_path = pandoc_path
        self.converted_count = 0
        self.error_count = 0

    def scan_md_files(self, directory):
        """递归扫描目录中的所有.md文件"""
        md_files = []
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith('.md'):
                        full_path = os.path.join(root, file)
                        md_files.append(full_path)
        except Exception as e:
            print(f"扫描目录时出错: {e}")
        return md_files

    def convert_md_to_html(self, md_file_path: str, md_input_directory: str, html_output_directory: str):
        """使用Pandoc将单个Markdown文件转换为HTML"""
        try:
            # 构建输出HTML文件路径
            html_file_path = md_file_path.replace('.md', '.html')
            if len(html_output_directory) > 0:
                html_file_path = html_file_path.replace(md_input_directory, html_output_directory)

            dir_path = os.path.dirname(html_file_path)
            os.makedirs(dir_path, exist_ok=True)

            # 构建Pandoc命令
            command = [
                self.pandoc_path,
                '-f', 'markdown',
                '-t', 'html',
                '-s',  # 生成独立HTML文件
                '--self-contained',
                '-o', html_file_path,
                md_file_path
            ]

            # 执行Pandoc转换
            result = subprocess.run(
                command,
                cwd=md_input_directory,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )

            print(f"✓ 转换成功: {md_file_path} -> {html_file_path}")
            self.converted_count += 1
            return True

        except subprocess.CalledProcessError as e:
            print(f"✗ 转换失败: {md_file_path} - {e} cmd:{command}")
            self.error_count += 1
            return False
        except Exception as e:
            print(f"✗ 处理文件时出错: {md_file_path} - {e} cmd:{command}")
            self.error_count += 1
            return False

    def batch_convert(self, input_directory, output_directory: str = ""):
        """批量转换目录中的所有Markdown文件"""
        # 检查Pandoc是否可用
        if not self.check_pandoc():
            print("错误: 无法找到或运行Pandoc，请检查路径配置")
            return False

        print(f"开始扫描目录: {input_directory}")
        md_files = self.scan_md_files(input_directory)

        if not md_files:
            print("未找到任何.md文件")
            return True

        if not isinstance(output_directory, str) or len(output_directory) == 0:
            output_directory = input_directory

        print(f"找到 {len(md_files)} 个Markdown文件, 准备转换输出到目录 {output_directory}")
        print("-" * 50)

        # 逐个转换文件
        for md_file in md_files:
            self.convert_md_to_html(md_file, input_directory, output_directory)

        # 输出转换统计
        print("-" * 50)
        print(f"转换完成!")
        print(f"成功: {self.converted_count} 个文件")
        print(f"失败: {self.error_count} 个文件")
        return True

    def check_pandoc(self):
        """检查Pandoc是否可用"""
        try:
            result = subprocess.run(
                [self.pandoc_path, '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pandoc_run_file = os.path.join(script_dir, "pandoc")
    
    if not os.path.isfile(pandoc_run_file):
        pandoc_run_file = os.path.join(script_dir, "pandoc.exe")
    
    if not os.path.isfile(pandoc_run_file):
        pandoc_run_file = "pandoc.exe"
    
    parser = argparse.ArgumentParser(
        description='递归扫描目录中的Markdown文件并使用Pandoc转换为HTML'
    )

    parser.add_argument(
        'input_directory',
        help='要扫描的目录路径'
    )

    parser.add_argument(
        '--pandoc',
        default=pandoc_run_file,
        help='Pandoc可执行文件路径 (默认: pandoc.exe)'
    )

    parser.add_argument(
        '--output_directory',
        default='',
        help='输出目录路径 (默认: 与源文件同目录)'
    )

    args = parser.parse_args()

    # 检查目录是否存在
    if not os.path.isdir(args.input_directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)

    if not os.path.isfile(args.pandoc):
        print('错误pandoc可执行程序不存在.')
        sys.exit(1)
    
    # 创建转换器实例
    converter = MarkdownConverter(args.pandoc)

    # 执行批量转换
    success = converter.batch_convert(args.input_directory, args.output_directory)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
