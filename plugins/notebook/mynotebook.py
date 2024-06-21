import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# 主窗口继承自QMainWindow
class MyNoteBook(QMainWindow):
    # 构造函数
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('日记本')
        self.resize(400, 300)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.setStyleSheet('background-color: black; color: white')
        # 嵌套的laytout布局
        layout = QHBoxLayout() # 水平 
        
        # 添加一个工具栏
        self.toolbar = self.addToolBar('File')
        self.new = QAction("新建", self)
        # 设置图标
        #self.new.setIcon(QIcon('icons/新建.png'))
        self.new.triggered.connect(self.createNew)
        
        #self.save = QAction(QIcon('icons/保存.png'), '保存', self)
        self.save = QAction( '保存', self)
        self.save.triggered.connect(self.saveFile)
        self.toolbar.addAction(self.new)
        self.toolbar.addAction(self.save)
                
        # 新建一个列表
        self.listview = QListView()
        # 记录选中的项目的索引
        self.selectedIndex = -1
        # 数据模型
        self.model = QStringListModel()
        # 获取日记列表
        fileList = os.listdir('mynotes')
        self.list = [a.split('.')[0] for a in fileList]
        # 填充数据
        self.model.setStringList(self.list)
        # view与model关联
        self.listview.setModel(self.model)
        # 关联列表点击事件
        self.listview.clicked.connect(self.getFile)
        # 右键菜单
        self.listview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listview.customContextMenuRequested.connect(self.mycontext)
        
        self.edit = QTextEdit()
        self.edit.setPlaceholderText('请输入内容')
        
        # 左右的比例是 1:3
        layout.addWidget(self.listview, stretch = 1)
        layout.addWidget(self.edit, stretch = 3)
        
        self.centralWidget.setLayout(layout)
        
    # 右键的上下文菜单，会传入一个pos位置参数
    def mycontext(self, pos):
        self.menu = QMenu()  # 创建一个上下文菜单
        rename = self.menu.addAction('重命名')
        #self.menu.addSeparator()
        remove = self.menu.addAction('删除')
        # 把位置映射到全局
        action = self.menu.exec_(self.listview.mapToGlobal(pos))
        if action == rename:
            print('rename')
            self.rename()
        if action == remove:
            print('remove')
            self.remove()
    
    # 重命名
    def rename(self):
        if self.listview.selectionModel().selection().indexes() == []:
            QMessageBox.warning(self, '警告!', '请选中后再进行重命名操作！')
            return 
        self.selectedIndex = self.listview.selectionModel().selection().indexes()[0].row()
        print('当前选中的是:{}'.format(self.list[self.selectedIndex]))
        filePath = 'mynotes/' + self.list[self.selectedIndex] + '.txt'
        text, okPressed = QInputDialog.getText(self, "Get text","Your name:", QLineEdit.Normal, "")
        if okPressed and text != '':
            QMessageBox.information(self,'确认？', '确定要进行修改吗？')
            self.list[self.selectedIndex] = text # 先更改数据中的名字
            self.model.setStringList(self.list)
            os.rename(filePath, 'mynotes/' + text + '.txt') # 再对文件进行重命名
    
    
    # 删除文件
    def remove(self):
        # 错误弹窗警告
        if self.listview.selectionModel().selection().indexes() == []:
            QMessageBox.warning(self, '警告！', '请选中后在进行删除操作！')
            return
        self.selectedIndex = self.listview.selectionModel().selection().indexes()[0].row()
        print('当前选中的是:{}'.format(self.list[self.selectedIndex]))
        yesOrNo = QMessageBox.question(self, '警告', '确定要删除"{}"文件吗'.format(self.list[self.selectedIndex]))
        # 是否确认要删除
        if yesOrNo == QMessageBox.No:
            return
        filePath = 'mynotes/' + self.list[self.selectedIndex] + '.txt'
        self.edit.clear()  # 清除右边输入框的文本
        os.remove(filePath) # 删除对应的文件
        self.list.pop(self.selectedIndex)  # 从列表中删除
        self.model.setStringList(self.list) # 重新赋值model的数据
        print('删除了{}'.format(self.selectedIndex))
    
    
    # 创建新的
    def createNew(self):
        text, okPressed = QInputDialog.getText(self, '新建日记', '请输入日记名')
        if okPressed == True:
            if text in self.list:
                QMessageBox.warning(self, '重复', '已存在相同名字的日记')
                return
            filePath = os.path.join('mynotes', text+'.txt')
            self.list.append(text)
            self.slectedIndex = self.list.index(text)
            self.model.setStringList(self.list)
            with open(filePath, 'w+') as f:
                self.edit.setText(f.read())
            
    # 保存文件
    def saveFile(self):
        if self.selectedIndex == -1:
            QMessageBox.warning(self, '警告', '请选择要保存的文件')
            return 
        text = self.edit.toPlainText() # 获取日记内容
        filePath = os.path.join('mynotes', self.list[self.selectedIndex]+'.txt')
        with open(filePath, 'w') as f:
            f.write(text)
        QMessageBox.information(self, '提示', '保存成功！')    
    
    # 读取文件
    def getFile(self, item):
        self.selectedIndex = item.row() # 获取所在的行
        filepath = os.path.join('mynotes', self.list[item.row()]+'.txt')
        # 会自动关闭文件
        with open(filepath) as f:
            self.edit.setText(f.read())
        
        

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MyNoteBook()
#     window.show()
#     sys.exit(app.exec_())