from utils.qrcManage.setting import defaultCfg, qrc, defaultRcc, ResourceCfg

defaultCfg.resource_dir = 'demo5_dir'


qrc.load()

demo_cfg = ResourceCfg('demo', 'demo5_dir/demo_cfg', py_qrc_prefix='demo')

rcc = demo_cfg.loadQrcRCC('demo_resource', demo_cfg)

resource = rcc.addResource('static')

txt123 = resource.file('123.txt')
txt123.awrite('\n123')


rcc.save()

# rcc.toPy()





