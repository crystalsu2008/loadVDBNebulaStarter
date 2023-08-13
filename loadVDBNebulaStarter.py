import maya.cmds as cmds
import os


directory = os.environ.get('NEBULAPATH')
if directory is None:
    os.environ['NEBULAPATH'] = 'D:/Work/QX/Nebula/VDB Nebula Starter'

def get_nebula_path(directory, name, idx, colortype, res, extension):
    sidx=f"{idx:03d}"
    nebuladir = f"{name}_{sidx}_{colortype}"
    nebulaname = f"{name}_{sidx}_{colortype}_{res}_Res.{extension}"
    full_path = os.path.join(directory, nebuladir, nebulaname)
    full_path.replace('\\', '/')
    return full_path

directory = os.environ.get('NEBULAPATH')
nebulaname = 'nebula'
idx = 2
colortype = 'orange_blue'
res = 'Low'
extension = 'vdb'

full_path = get_nebula_path(directory, nebulaname, idx, colortype, res, extension)
print(full_path)


# 创建一个 aiVolume 节点
aiVolumeNode = cmds.createNode('aiVolume')

# 设置 aiVolume 节点的属性
# cmds.setAttr(aiVolumeNode + '.stepSize', 0.1)
# cmds.setAttr(aiVolumeNode + '.volumePadding', 0.1)
cmds.setAttr(aiVolumeNode + '.filename', full_path, type="string")
cmds.setAttr(aiVolumeNode + '.grids', "Cd density", type="string")


# 创建一个 aiStandardVolume 材质节点
'''
aiStandardVolumeNode = cmds.shadingNode('aiStandardVolume', asShader=True)

# 连接 aiVolume 节点和 aiStandardVolume 节点
cmds.connectAttr(aiVolumeNode + '.outColor', aiStandardVolumeNode + '.color')

# 创建一个材质球
shadingGroup = cmds.sets(renderable=True, noVolumeShader=True, empty=True)

# 将 aiStandardVolume 节点连接到材质球
cmds.connectAttr(aiStandardVolumeNode + '.outColor', shadingGroup + '.volumeShader')

# 创建一个立方体
cube = cmds.polyCube()[0]

# 将材质球应用于立方体
cmds.sets(cube, edit=True, forceElement=shadingGroup)
'''