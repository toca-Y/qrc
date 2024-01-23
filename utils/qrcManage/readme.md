
+ 原理: 通过`pyrcc5.exe`将.qrc文件转为.py文件, 且通过`import`的方式进行导入, 当导入之后资源文件就可以通过PyQt进行调用, 也可以通过`QResource`直接读取资源文件内容:
+ 使用方法(资源文件转为`py`文件使用方法)
  + 方式一: 直接使用 
    ```python
    import resource  # resource.qrc -> resource.py
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QLabel
    
    resource_path = ":/static/test/a.png"
    label = QLabel()
    icon = QIcon(resource_path)
    label.setPixmap(icon.pixmap(label.size()))
    
    ```

  + 方式二: 通过QResource进行读取数据
    ```python
    
    import resource  # resource.qrc -> resource.py
    from PyQt5.QtCore import QResource
    
    resource_path = ":/static/test/a.png"
    data = QResource(resource_path).data()
    print(data)  # = open('a.png', 'rb').read()
    ```

+ 应用
  + 