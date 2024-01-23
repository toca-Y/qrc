import xml.etree.ElementTree as ET
from pathlib import Path


def load_qt_qrc(qrc_file) -> dict:
    res_data = {}
    tree = ET.parse(qrc_file)
    root = tree.getroot()
    for prefix_child in root:
        prefix = prefix_child.get('prefix')
        files = res_data.setdefault(prefix, [])
        for file in prefix_child:
            text = file.text
            files.append(text)
    return res_data


def save_qt_qrc(source_json, filename):
    qresource_name = 'qresource'
    root = ET.Element("RCC")
    
    for prefix, files in source_json.items():
        prefix_child = ET.SubElement(root, qresource_name)
        prefix_child.set('prefix', prefix)
        for file in files:
            file_child = ET.SubElement(prefix_child, 'file')
            file_child.text = file
    
    tree = ET.ElementTree(root)
    tree.write(filename)


if __name__ == '__main__':
    """
    Main run
    """
    data = load_qt_qrc(r'E:\casuallyToDo\utils\qrcManage\local.qrc')
    