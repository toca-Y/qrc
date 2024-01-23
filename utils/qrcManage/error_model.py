import traceback


class PrintExc:
    _enable = True
    
    def __call__(self, *args, **kwargs):
        if self.enable:
            traceback.print_exc(*args, **kwargs)
    
    @property
    def enable(self):
        return self._enable
    
    @enable.setter
    def enable(self, value):
        self._enable = value


printExc = PrintExc()


class _BaseException(Exception):
    msg = None
    
    def __init__(self, msg=None, *args, **kwargs):
        msg = msg or self.msg
        super().__init__(msg, *args)


class ConfigFileNotExists(_BaseException):
    msg = '配置文件不存在'


class ConfigReadError(_BaseException):
    msg = '配置读取失败'


class ConfigWriteError(_BaseException):
    msg = '配置写入失败'


class PyRccFileNotExists(_BaseException):
    msg = 'PyRcc文件(.py)不存在'
    
    def __init__(self, cfg_name=None, rcc_name=None, *args, **kwargs):
        msg = self.msg + f'(cfg){cfg_name}-(rcc){rcc_name}'
        super().__init__(msg, *args, **kwargs)


class PyRccImportError(_BaseException):
    msg = 'PyRcc导入失败'


class QRCFileNotExists(_BaseException):
    msg = 'QRC文件不存在'


class QRCFileReadError(_BaseException):
    msg = 'QRC文件读取失败'


if __name__ == '__main__':
    """
    Main run
    """
