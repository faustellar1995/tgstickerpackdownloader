import os
import subprocess
from PyQt5.QtWidgets import (QWidget, QComboBox, QPushButton, 
                            QHBoxLayout, QFileDialog)
from PyQt5.QtCore import QStandardPaths

class DirManager:
    def __init__(self, filename="dirs.txt"):
        # 获取用户主目录
        home = os.path.expanduser("~")
        # 创建pyqt目录
        self.pyqt_dir = os.path.join(home, "pyqt")
        os.makedirs(self.pyqt_dir, exist_ok=True)
        # 设置文件路径
        self.filepath = os.path.join(self.pyqt_dir, filename)
        # 初始化目录列表
        self.dir_list = []
        self.load_dirs()

    def load_dirs(self):
        """从文件加载目录列表"""
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.dir_list = [line.strip() for line in f.readlines()]
        else:
            self.dir_list = []

    def save_dirs(self):
        """保存目录列表到文件"""
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(self.dir_list))

    def add_dir(self, dir_path):
        """添加新目录"""
        if dir_path and dir_path not in self.dir_list:
            self.dir_list.append(dir_path)
            self.save_dirs()

    def get_dirs(self):
        """获取目录列表"""
        return self.dir_list

    def set_current_dir(self, dir_path):
        """设置当前目录"""
        if dir_path in self.dir_list:
            # 将当前目录移到列表最前面
            self.dir_list.remove(dir_path)
            self.dir_list.insert(0, dir_path)
            self.save_dirs()

    def open_dir(self, dir_path):
        """使用系统文件浏览器打开目录"""
        if os.path.exists(dir_path):
            if os.name == 'nt':  # Windows
                os.startfile(dir_path)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.call(['open', dir_path] if sys.platform == 'darwin' else ['xdg-open', dir_path])

class DirManagerUI(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.init_ui()

    def init_ui(self):
        # 创建水平布局
        layout = QHBoxLayout(self)

        # 创建ComboBox
        self.combo = QComboBox(self)
        self.combo.addItems(self.manager.get_dirs())
        self.combo.currentTextChanged.connect(self.on_dir_changed)
        layout.addWidget(self.combo, stretch=1)

        # 创建Browse按钮
        self.browse_btn = QPushButton("Browse...", self)
        self.browse_btn.setMaximumWidth(100)
        self.browse_btn.clicked.connect(self.on_browse)
        layout.addWidget(self.browse_btn)

        # 创建Open按钮
        self.open_btn = QPushButton("Open", self)
        self.open_btn.setMaximumWidth(100)
        self.open_btn.clicked.connect(self.on_open)
        layout.addWidget(self.open_btn)

        # 设置布局
        self.setLayout(layout)
        self.setMinimumWidth(400)

    def on_dir_changed(self, dir_path):
        """当ComboBox选择改变时"""
        self.manager.set_current_dir(dir_path)

    def on_browse(self):
        """点击Browse按钮时"""
        # 获取用户选择的文件夹
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder",
            QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        )
        if folder:
            # 将选择的文件夹路径添加到目录列表
            self.manager.add_dir(folder)
            # 更新ComboBox
            self.combo.clear()
            self.combo.addItems(self.manager.get_dirs())
            self.combo.setCurrentText(folder)

    def on_open(self):
        """点击Open按钮时"""
        dir_path = self.combo.currentText()
        self.manager.open_dir(dir_path)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    
    # 创建管理器和UI
    manager = DirManager()
    ui = DirManagerUI(manager)
    
    # 显示窗口
    ui.setWindowTitle("Directory Manager")
    ui.show()
    
    sys.exit(app.exec_())
