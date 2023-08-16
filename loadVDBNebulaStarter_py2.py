from __future__ import absolute_import
import maya.cmds as cmds
import os

def vns_setNEBULAPATHScriptNode(path):
    script_node_name = u'nebula_initial_settingsScriptNode'
    script_node = cmds.ls(script_node_name)
    if not script_node:
        script_node = cmds.scriptNode(name=script_node_name, sourceType=u'python', scriptType=2)
    else:
        script_node = script_node[0]
    script = u'import os\nos.environ["NEBULAPATH"] = "{}"'.format(path)
    cmds.scriptNode(script_node, edit=True, beforeScript=script)

def vns_select_directory(*args):
    directory = cmds.fileDialog2(fileMode=3, dialogStyle=2)
    if directory:
        cmds.textField(vns_directory_text_field, edit=True, text=directory[0])
        os.environ[u'NEBULAPATH'] = directory[0]
        vns_setNEBULAPATHScriptNode(directory[0])

def vns_populate_shader_menu(menu, suffix):
    cmds.optionMenu(menu, edit=True, deleteAllItems=True)
    shaders = cmds.ls(type=u'aiStandardVolume')
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

def vns_get_param_from_ctrls(*args):
    info = {}
    info[u'directory'] = cmds.textField(vns_directory_text_field, query=True, text=True)
    info[u'nebula_name'] = cmds.textField(vns_nebula_text_field, query=True, text=True)
    info[u'index'] = cmds.intField(vns_index_int_field, query=True, value=True)
    info[u'color_type'] = cmds.optionMenu(vns_color_type_option_menu, query=True, value=True)
    info[u'resolution'] = cmds.optionMenu(vns_resolution_option_menu, query=True, value=True)
    info[u'nebula_shader'] = cmds.optionMenu(vns_nebula_shader_option_menu, query=True, value=True)
    info[u'fog_shader'] = cmds.optionMenu(vns_fog_shader_option_menu, query=True, value=True)
    return info

def vns_get_nebula_path(**kwargs):
    name = kwargs[u'nebula_name']
    idx = kwargs[u'index']
    typ = kwargs[u'type']
    colortype = kwargs[u'color_type']
    res = kwargs[u'resolution']
    extension = u"vdb"

    sidx="%03d" % idx
    nebuladir = f"{name}_{sidx}_{colortype}"
    nebulaname = f"{name}_{sidx}_{colortype}_{res}_Res.{extension}"
    if typ == u'fog':
        nebuladir = f"{name}_{sidx}_orange_blue"
        nebulaname = f"{name}_{sidx}_orange_blue_Fog.{extension}"
    elif typ == u'proxy':
        nebulaname = f"{name}_{sidx}_{colortype}_proxy.obj"
    full_path = os.path.join(nebuladir, nebulaname)
    full_path = full_path.replace(u'\\', u'/')
    return full_path

def vns_import_proxy(**kwargs):
    nebula_name = kwargs[u'nebula_name']
    sidx=f"{kwargs['index']:03d}"
    nebulaProxyName = f"{nebula_name}_{sidx}"
    # 检查新名称是否已经存在
    while cmds.objExists(f"{nebulaProxyName}_proxy"):
        # 如果新名称已经存在，则更改新名称
        nebulaProxyName += u"_1"
    nebulaProxyName = f"{nebulaProxyName}_proxy"

    # 导入 proxy 物体
    kwargs[u'type'] = u'proxy'
    full_path = os.environ.get(u'NEBULAPATH')+u'/'+vns_get_nebula_path(**kwargs)
    # 获取导入 OBJ 文件之前的多边形物体列表
    polyObjectsBefore = cmds.ls(type=u"mesh")

    # 导入 OBJ 文件
    cmds.file(full_path, i=True, type=u"OBJ", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace=u":", options=u"mo=1")

    # 获取导入 OBJ 文件之后的多边形物体列表
    polyObjectsAfter = cmds.ls(type=u"mesh")

    # 计算两次获取的多边形物体列表的差集，得到刚刚导入的几何体
    importedObjects = list(set(polyObjectsAfter) - set(polyObjectsBefore))

    # 创建一个空列表，用于存储 transform 结点名称
    transformNodes = []

    # 获取刚刚导入的几何体的 transform 结点名称，并将它们添加到列表中
    for obj in importedObjects:
        transformNode = cmds.listRelatives(obj, parent=True)[0]
        transformNode = cmds.rename(transformNode, nebulaProxyName)
        transformNodes.append(transformNode)
        cmds.parent(transformNode, kwargs[u'nebula_grp'])

    # 检查场景中是否存在名为 "nebula_proxy" 的显示层
    if not cmds.objExists(u"nebula_proxy"):
        # 如果不存在，则创建一个新的显示层
        cmds.createDisplayLayer(name=u"nebula_proxy")
        # 将此 layer 的 display type 设置为 template
        cmds.setAttr(u"nebula_proxy.displayType", 1)

    # 将 nebula proxy 加入名为 "nebula_proxy" 的显示层
    cmds.editDisplayLayerMembers(u"nebula_proxy", transformNodes[-1])
    return transformNodes

def vns_create_nebula_volume(**kwargs):
    nebula_name = kwargs[u'nebula_name']
    sidx=f"{kwargs['index']:03d}"

    # 创建 nebula 节点
    nebulaGrpName = f"{nebula_name}_{sidx}"
    nebulaVolName = f"{nebula_name}_{sidx}_vdb"
    nebulaFogName = f"{nebula_name}_{sidx}_fog"

    nebulaGrpTran = cmds.createNode(u'transform', n=nebulaGrpName)
    nebulaVolumeTran = cmds.createNode(u'transform', n=nebulaVolName, p=nebulaGrpTran)
    nebulaVolumeNode = cmds.createNode(u'aiVolume', n=f"{nebulaVolName}Shape", p=nebulaVolumeTran)
    nebulaFogTran = cmds.createNode(u'transform', n=nebulaFogName, p=nebulaGrpTran)
    nebulaFogNode = cmds.createNode(u'aiVolume', n=f"{nebulaFogName}Shape", p=nebulaFogTran)

    # 检查场景中是否存在名为 "nebula_vdb" 的显示层
    if not cmds.objExists(u"nebula_vdb"):
        # 如果不存在，则创建一个新的显示层
        cmds.createDisplayLayer(name=u"nebula_vdb")

    # 将 nebula VDB 加入名为 "nebula_vdb" 的显示层
    cmds.editDisplayLayerMembers(u"nebula_vdb", nebulaVolumeTran)

     # 检查场景中是否存在名为 "nebula_fog" 的显示层
    if not cmds.objExists(u"nebula_fog"):
        # 如果不存在，则创建一个新的显示层
        cmds.createDisplayLayer(name=u"nebula_fog")

    # 将 nebula Fog 加入名为 "nebula_fog" 的显示层
    cmds.editDisplayLayerMembers(u"nebula_fog", nebulaFogTran)

    # 设置 nebula aiVolume 节点的属性
    kwargs[u'type'] = u'vol'
    full_path = u'$NEBULAPATH/'+vns_get_nebula_path(**kwargs)
    # cmds.setAttr(aiVolumeNode + '.stepSize', 0.1)
    # cmds.setAttr(aiVolumeNode + '.volumePadding', 0.1)
    cmds.setAttr(nebulaVolumeNode + u'.filename', full_path, type=u"string")
    cmds.setAttr(nebulaVolumeNode + u'.grids', u"Cd density", type=u"string")
    # 连接材质
    shadingGroups = cmds.listConnections(kwargs[u'nebula_shader'], type=u'shadingEngine')
    cmds.sets(nebulaVolumeNode, edit=True, forceElement=shadingGroups[0])

    # 设置 fog aiVolume 节点的属性
    kwargs[u'type'] = u'fog'
    full_path = u'$NEBULAPATH/'+vns_get_nebula_path(**kwargs)
    # cmds.setAttr(aiVolumeNode + '.stepSize', 0.1)
    # cmds.setAttr(aiVolumeNode + '.volumePadding', 0.1)
    cmds.setAttr(nebulaFogNode + u'.filename', full_path, type=u"string")
    cmds.setAttr(nebulaFogNode + u'.grids', u"density", type=u"string")
    # 连接材质
    shadingGroups = cmds.listConnections(kwargs[u'fog_shader'], type=u'shadingEngine')
    cmds.sets(nebulaFogNode, edit=True, forceElement=shadingGroups[0])

    # 导入 proxy 物体
    kwargs[u'nebula_grp'] = nebulaGrpTran
    vns_import_proxy(**kwargs)

def vns_get_nebula_element(nebulaGrp, suffix):
    # 检查后缀是否有效
    if suffix not in [u"vdb", u"fog", u"proxy"]:
        cmds.warning(u"Invalid suffix")
        return []

    # 根据后缀确定要搜索的物体类型
    objectType = u"aiVolume" if suffix in [u"vdb", u"fog"] else u"mesh"

    # 获取指定名称的组
    selectedGroup = cmds.ls(nebulaGrp, type=u"transform")

    # 检查是否存在指定名称的组
    if len(selectedGroup) != 1:
        cmds.warning(u"Group not found")
        return []

    # 获取组中的所有指定类型的物体
    objects = cmds.listRelatives(selectedGroup[0], allDescendents=True, type=objectType)

    # 创建一个空列表，用于存储符合条件的 transform 结点名称
    result = []

    # 遍历物体，找出 transform 结点名称最后以给定后缀结尾的物体
    for obj in objects:
        # 获取物体的 transform 结点名称
        transformNode = cmds.listRelatives(obj, parent=True)[0]

        # 检查 transform 结点名称是否以给定后缀结尾
        if transformNode.endswith(suffix):
            result.append((obj, transformNode))

    return result

def vns_getFileInfo(filePath):
    parentDir = os.environ.get(u'NEBULAPATH')
    if not filePath.startswith(u'$NEBULAPATH'):
        parentDir = os.path.dirname(os.path.dirname(os.path.abspath(filePath)))

    # 获取文件名（不带路径和后缀）
    fileName = os.path.splitext(os.path.basename(filePath))[0]

    # 以 '_' 字符分隔文件名
    parts = fileName.split(u'_')

    # 获取 'nebula_name' 属性
    nebula_name = parts[0]

    # 获取 'index' 属性
    index = int(parts[1])

    # 获取 'color_type' 属性
    color_type = None
    if u"orange" in fileName and u"blue" in fileName:
        color_type = u"orange_blue"
    elif u"blue" in fileName and u"purple" in fileName:
        color_type = u"blue_purple"
    elif u"pink" in fileName and u"purple" in fileName:
        color_type = u"pink_purple"
    elif u"black" in fileName and u"white" in fileName:
        color_type = u"black_white"

    # 获取 'resolution' 属性
    resolution = None
    if u"High" in fileName:
        resolution = u"High"
    elif u"Mid" in fileName:
        resolution = u"Mid"
    elif u"Qrt" in fileName:
        resolution = u"Qrt"
    elif u"Low" in fileName:
        resolution = u"Low"

    # 以字典数据存储以上数据并返回
    return {
        u'directory': parentDir,
        u'nebula_name': nebula_name,
        u'index': index,
        u'color_type': color_type,
        u'resolution': resolution
    }

def vns_getAiVolumeShader(transformName):
    # 获取 transform 结点的 shape 结点
    shapeNode = cmds.listRelatives(transformName, shapes=True)[0]

    # 获取 shape 结点的 shadingEngine
    shadingEngine = cmds.listConnections(shapeNode, type=u"shadingEngine")

    # 检查是否找到了 shadingEngine
    if shadingEngine is not None and len(shadingEngine) > 0:
        # 获取 shadingEngine 的 volumeShader 连接
        volumeShader = cmds.listConnections(shadingEngine[0] + u".volumeShader")

        # 检查是否找到了 volumeShader
        if volumeShader is not None and len(volumeShader) > 0:
            # 返回 surfaceShader 的名称
            return volumeShader[0]

    # 如果没有找到 aiStandardShader，则返回 None
    return None

def vns_get_param_from_selected(*args):
    # 获取当前选择的组
    selectedGroup = cmds.ls(selection=True, type=u"transform")

    # 检查是否选择了一个组
    if len(selectedGroup) != 1:
        cmds.warning(u"Please select a group")
    else:
        # 获取组中的 nebula vdb 物体
        vdb, vdbtrans = vns_get_nebula_element(selectedGroup, u"vdb")[0]
        fog, fogtrans = vns_get_nebula_element(selectedGroup, u"fog")[0]

    filePath = cmds.getAttr(vdb + u".filename")
    info = vns_getFileInfo(filePath)

    info[u'nebula_shader'] = vns_getAiVolumeShader(vdb)
    info[u'fog_shader'] = vns_getAiVolumeShader(fog)

    return info

def vns_set_param_to_ctrls(**kwargs):
    cmds.textField(vns_directory_text_field, edit=True, text=kwargs[u'directory'])
    os.environ[u'NEBULAPATH'] = kwargs[u'directory']
    vns_setNEBULAPATHScriptNode(kwargs[u'directory'])
    cmds.textField(vns_nebula_text_field, edit=True, text=kwargs[u'nebula_name'])
    cmds.intField(vns_index_int_field, edit=True, value=kwargs[u'index'])
    cmds.optionMenu(vns_color_type_option_menu, edit=True, value=kwargs[u'color_type'])
    cmds.optionMenu(vns_resolution_option_menu, edit=True, value=kwargs[u'resolution'])
    cmds.optionMenu(vns_nebula_shader_option_menu, edit=True, value=kwargs[u'nebula_shader'])
    cmds.optionMenu(vns_fog_shader_option_menu, edit=True, value=kwargs[u'fog_shader'])

def vns_replace_selected_nebula(**kwargs):
    # 获取当前选择的组
    selectedGroup = cmds.ls(selection=True, type=u"transform")

    # 检查是否选择了一个组
    if len(selectedGroup) != 1:
        cmds.warning(u"Please select a group")
    else:
        # 获取组中的 nebula vdb 物体
        kwargs[u'nebula_grp'] = selectedGroup[0]
        vdb, vdbtrans = vns_get_nebula_element(selectedGroup, u"vdb")[0]
        fog, fogtrans = vns_get_nebula_element(selectedGroup, u"fog")[0]
        proxy, proxytrans = vns_get_nebula_element(selectedGroup, u"proxy")[0]
    
    kwargs[u'type'] = u'vol'
    full_path = u'$NEBULAPATH/'+vns_get_nebula_path(**kwargs)
    cmds.setAttr(vdb + u'.filename', full_path, type=u"string")
    # 连接材质
    shadingGroups = cmds.listConnections(kwargs[u'nebula_shader'], type=u'shadingEngine')
    cmds.sets(vdb, edit=True, forceElement=shadingGroups[0])

    kwargs[u'type'] = u'fog'
    full_path = u'$NEBULAPATH/'+vns_get_nebula_path(**kwargs)
    cmds.setAttr(fog + u'.filename', full_path, type=u"string")
    # 连接材质
    shadingGroups = cmds.listConnections(kwargs[u'fog_shader'], type=u'shadingEngine')
    cmds.sets(fog, edit=True, forceElement=shadingGroups[0])
    
    # 导入 proxy 物体
    matrix = cmds.xform(proxytrans, query=True, matrix=True, worldSpace=True)
    cmds.delete(proxytrans)
    proxy_trans = vns_import_proxy(**kwargs)
    cmds.xform(proxy_trans, matrix=matrix, worldSpace=True)

def vns_create_nebula(*args):
    info = vns_get_param_from_ctrls()
    vns_create_nebula_volume(**info)
    print u'Create!'

def vns_set_ctrls_from_selected(*args):
    info = vns_get_param_from_selected()
    vns_set_param_to_ctrls(**info)
    print u'get info from select!'

def vns_replace_selected(*args):
    info = vns_get_param_from_ctrls()
    vns_replace_selected_nebula(**info)
    print u'Replace Selected!'

vns_window = cmds.window(title=u"VDB Nebula Starter")
vns_layout = cmds.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 80), (2, 150), (3, 100)], adjustableColumn=2)
vns_directory_label = cmds.text(label=u"File Dir:")
vns_directory = os.environ.get(u'NEBULAPATH')
vns_directory_text_field = cmds.textField(text=vns_directory)
vns_directory_button = cmds.button(label=u"Select Directory", command=vns_select_directory)
vns_nebula_label = cmds.text(label=u"Nebula Name:")
vns_nebula_text_field = cmds.textField(text=u"nebula")
vns_empty_text_1 = cmds.text(label=u"")
vns_index_label = cmds.text(label=u"Index:")
vns_index_int_field = cmds.intField(value=1)
vns_empty_text_2 = cmds.text(label=u"")
vns_color_type_label = cmds.text(label=u"Color Type:")
vns_color_type_option_menu = cmds.optionMenu()
cmds.menuItem(label=u"orange_blue")
cmds.menuItem(label=u"blue_purple")
cmds.menuItem(label=u"pink_purple")
cmds.menuItem(label=u"black_white")
vns_empty_text_3 = cmds.text(label=u"")
vns_resolution_label = cmds.text(label=u"Resolution:")
vns_resolution_option_menu = cmds.optionMenu()
cmds.menuItem(label=u"Low")
cmds.menuItem(label=u"Qrt")
cmds.menuItem(label=u"Mid")
cmds.menuItem(label=u"High")
vns_empty_text_4 = cmds.text(label=u"")
vns_nebula_shader_label = cmds.text(label=u"Nebula Shader:")
vns_nebula_shader_option_menu = cmds.optionMenu()
vns_populate_shader_menu(vns_nebula_shader_option_menu, u'vdb')
vns_empty_text_5 = cmds.text(label=u"")
vns_fog_shader_label = cmds.text(label=u"Fog Shader:")
vns_fog_shader_option_menu = cmds.optionMenu()
vns_populate_shader_menu(vns_fog_shader_option_menu, u'fog')
vns_empty_text_6 = cmds.text(label=u"")
vns_create_button = cmds.button(label=u"Create", command=vns_create_nebula)
vns_get_info_button = cmds.button(label=u"Get Parameter From Selected", command=vns_set_ctrls_from_selected)
vns_replace_button = cmds.button(label=u"Replace Selected", command=vns_replace_selected)
cmds.showWindow(vns_window)