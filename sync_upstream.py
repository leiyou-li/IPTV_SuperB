import os
import subprocess
import logging
import time
from datetime import datetime
import shutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sync.log", "w", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def check_upstream_changes():
    """检查上游仓库是否有更新"""
    try:
        # 获取当前分支的上游远程仓库信息
        subprocess.run(['git', 'remote', 'update'], check=True)
        result = subprocess.run(['git', 'status', '-uno'], capture_output=True, text=True)
        
        if 'Your branch is behind' in result.stdout:
            return True
        return False
    except subprocess.CalledProcessError as e:
        logging.error(f"检查上游更新时出错: {e}")
        return False

def backup_demo_file():
    """备份demo.txt文件"""
    try:
        if os.path.exists('demo.txt'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            # 备份当前demo.txt
            shutil.copy2('demo.txt', f'{backup_dir}/demo_{timestamp}.txt')
            # 创建最新备份的软链接
            if os.path.exists(f'{backup_dir}/demo_latest.txt'):
                os.remove(f'{backup_dir}/demo_latest.txt')
            os.symlink(f'demo_{timestamp}.txt', f'{backup_dir}/demo_latest.txt')
            logging.info("demo.txt文件已备份")
    except Exception as e:
        logging.error(f"备份demo.txt文件时出错: {e}")

def sync_with_upstream():
    """同步上游仓库的更新"""
    try:
        # 1. 备份demo.txt
        backup_demo_file()
        
        # 2. 获取上游更新
        subprocess.run(['git', 'fetch', 'upstream'], check=True)
        subprocess.run(['git', 'checkout', 'main'], check=True)
        subprocess.run(['git', 'merge', 'upstream/main'], check=True)
        
        # 3. 恢复demo.txt
        if os.path.exists('backups/demo_latest.txt'):
            # 删除上游的demo.txt
            if os.path.exists('demo.txt'):
                os.remove('demo.txt')
            # 恢复备份的demo.txt
            shutil.copy2('backups/demo_latest.txt', 'demo.txt')
            logging.info("demo.txt文件已恢复")
        
        logging.info("成功同步上游更新")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"同步上游更新时出错: {e}")
        return False

def main():
    """主函数"""
    logging.info("开始检查上游更新...")
    
    if check_upstream_changes():
        logging.info("检测到上游有更新，开始同步...")
        if sync_with_upstream():
            logging.info("同步完成")
        else:
            logging.error("同步失败")
    else:
        logging.info("当前已是最新版本，无需更新")

if __name__ == "__main__":
    main() 