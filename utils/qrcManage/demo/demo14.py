import xml.etree.ElementTree as ET
from utils.qrcManage.demo.demo1 import PyRcc

py_rcc = PyRcc(check_exists=False)
py_file_path = rf'qrcResource\defaultCfg\qrc_icon\qrc_qrc_icon.py'
py_rcc.loadPy(py_file_path)

xml = py_rcc.xml

tree = ET.ElementTree(xml)

tree.write('output_qrc.qrc')


