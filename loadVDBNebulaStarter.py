import maya.cmds as cmds
import os

def select_directory(*args):
    directory = cmds.fileDialog2(fileMode=3, dialogStyle=2)
    if directory:
        cmds.textField(directory_text_field, edit=True, text=directory[0])
        os.environ['NEBULAPATH'] = directory[0]

def populate_shader_menu(menu, suffix):
    cmds.optionMenu(menu, edit=True, deleteAllItems=True)
    shaders = cmds.ls(type='aiStandardVolume')
    default_shader = None
    for shader in shaders:
        if shader.endswith(suffix):
            default_shader = shader
            break
    if not default_shader and shaders:
        default_shader = shaders[0]
    for shader in shaders:
        cmds.menuItem(label=shader, parent=menu)
    if default_shader:
        cmds.optionMenu(menu, edit=True, value=default_shader)

def get_param_from_ctrls(*args):
    info = {}
    info['directory'] = cmds.textField(directory_text_field, query=True, text=True)
    info['nebula_name'] = cmds.textField(nebula_text_field, query=True, text=True)
    info['index'] = cmds.intField(index_int_field, query=True, value=True)
    info['color_type'] = cmds.optionMenu(color_type_option_menu, query=True, value=True)
    info['resolution'] = cmds.optionMenu(resolution_option_menu, query=True, value=True)
    info['nebula_shader'] = cmds.optionMenu(nebula_shader_option_menu, query=True, value=True)
    info['fog_shader'] = cmds.optionMenu(fog_shader_option_menu, query=True, value=True)
    return info

def vns_get_nebula_path(**kwargs):
    name = kwargs['nebula_name']
    idx = kwargs['index']
    typ = kwargs['type']
    colortype = kwargs['color_type']
    res = kwargs['resolution']
    extension = "vdb"

    sidx=f"{idx:03d}"
    nebuladir = f"{name}_{sidx}_{colortype}"
    nebulaname = f"{name}_{sidx}_{colortype}_{res}_Res.{extension}"
    if typ == 'fog':
        nebuladir = f"{name}_{sidx}_orange_blue"
        nebulaname = f"{name}_{sidx}_orange_blue_Fog.{extension}"
    full_path = os.path.join(nebuladir, nebulaname)
    full_path = full_path.replace('\\', '/')
    return full_path

def vnd_create_nebula_volume(**kwargs):
    nebula_name = kwargs['nebula_name']
    sidx=f"{kwargs['index']:03d}"

    # 创建 nebula 节点
    nebulaGrpName = f"{nebula_name}_{sidx}"
    nebulaVolName = f"{nebula_name}_{sidx}_vdb"
    nebulaFogName = f"{nebula_name}_{sidx}_fog"

    nebulaGrpTran = cmds.createNode('transform', n=nebulaGrpName)
    nebulaVolumeTran = cmds.createNode('transform', n=nebulaVolName, p=nebulaGrpTran)
    nebulaVolumeNode = cmds.createNode('aiVolume', n=f"{nebulaVolName}Shape", p=nebulaVolumeTran)

    kwargs['type'] = 'vol'
    full_path = '$NEBULAPATH/'+vns_get_nebula_path(**kwargs)

    # 设置 aiVolume 节点的属性
    # cmds.setAttr(aiVolumeNode + '.stepSize', 0.1)
    # cmds.setAttr(aiVolumeNode + '.volumePadding', 0.1)
    cmds.setAttr(nebulaVolumeNode + '.filename', full_path, type="string")
    cmds.setAttr(nebulaVolumeNode + '.grids', "Cd density", type="string")

def create_nebula(*args):
    info = get_param_from_ctrls()
    vnd_create_nebula_volume(**info)
    print(info)
    print('Create!')

def get_info_from_selected(*args):
    print('get info from select!')

def refresh_selected(*args):
    print('Refresh Selected!')

window = cmds.window(title="Select Directory")
layout = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 80), (2, 150), (3, 100)], adjustableColumn=2)
directory_label = cmds.text(label="File Dir:")
directory = os.environ.get('NEBULAPATH')
directory_text_field = cmds.textField(text=directory)
directory_button = cmds.button(label="Select Directory", command=select_directory)
nebula_label = cmds.text(label="Nebula Name:")
nebula_text_field = cmds.textField(text="nebula")
empty_text_1 = cmds.text(label="")
index_label = cmds.text(label="Index:")
index_int_field = cmds.intField(value=1)
empty_text_2 = cmds.text(label="")
color_type_label = cmds.text(label="Color Type:")
color_type_option_menu = cmds.optionMenu()
cmds.menuItem(label="orange_blue")
cmds.menuItem(label="blue_purple")
cmds.menuItem(label="pink_purple")
cmds.menuItem(label="black_white")
empty_text_3 = cmds.text(label="")
resolution_label = cmds.text(label="Resolution:")
resolution_option_menu = cmds.optionMenu()
cmds.menuItem(label="Low")
cmds.menuItem(label="Qrt")
cmds.menuItem(label="Mid")
cmds.menuItem(label="High")
empty_text_4 = cmds.text(label="")
nebula_shader_label = cmds.text(label="Nebula Shader:")
nebula_shader_option_menu = cmds.optionMenu()
populate_shader_menu(nebula_shader_option_menu, 'vdb')
empty_text_5 = cmds.text(label="")
fog_shader_label = cmds.text(label="Fog Shader:")
fog_shader_option_menu = cmds.optionMenu()
populate_shader_menu(fog_shader_option_menu, 'fog')
empty_text_6 = cmds.text(label="")
create_button = cmds.button(label="Create", command=create_nebula)
get_info_button = cmds.button(label="Get Parameter From Selected", command=get_info_from_selected)
refresh_button = cmds.button(label="Refresh Selected", command=refresh_selected)
cmds.showWindow(window)


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