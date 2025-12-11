from maya import cmds
from maya.api import OpenMaya as om2
import re


INDEX_PATTERN = r"(.*)\[(\d+)\]"


def get_node(item):
    return item.split(".")[0]


def get_index(item):
    """Retrieves the index of an item such as a vertex or face.

    Args:
    - item (str): the item as a string.

    Returns:
    - int/None: stripped index from the item."""

    match = re.match(INDEX_PATTERN, item)

    if match:
        _, index = match.groups()
        return int(index)

    raise ValueError(f"Invalid index pattern: {item}")


def get_dependency_node(node):
    """Retrieves the corresponding MObject representing the node's dependency node.
    This MObject can then be used with other OpenMaya API functions to manipulate
    the node.

    Args:
    - node (str): The name of the node for which the dependency node is required.

    Returns:
    - OpenMaya.MObject: The dependency node associated with the specified node."""

    selection = om2.MSelectionList()
    selection.add(node)
    return selection.getDependNode(0)


def get_DAG_path(node):
    """Retrieves the corresponding MDagPath representing the node's DAG path.
    This MDagPath can then be used with other OpenMaya API functions to manipulate
    the node.

    Args:
    - node (str): The name of the node for which the DAG path is required.

    Returns:
    - OpenMaya.MDagPath: The DAG path associated with the specified node."""

    selection = om2.MSelectionList()
    selection.add(node)

    return selection.getDagPath(0)


def get_face_normal(face):
    mesh, face = face.split(".")
    face_index = get_index(face)

    DAG_path = get_DAG_path(mesh)
    mesh_polygon_fn = om2.MFnMesh(DAG_path)

    normal = mesh_polygon_fn.getPolygonNormal(face_index)
    return normal.x, normal.y, normal.z


def get_point_order(mesh):
    """Yields vertex indices for a given mesh in the order they are stored
    in the mesh's data structure.

    Args:
    - mesh (str): The name of the mesh whose vertex indices are to be retrieved.

    Yields:
    - int: The index of each vertex in the order it is stored in the mesh."""

    shape = cmds.listRelatives(mesh, shapes=True)[0]
    dependency_node = get_dependency_node(shape)
    mesh_fn = om2.MFnMesh(dependency_node)

    _, vertex_list = mesh_fn.getVertices()

    for vertex_index in vertex_list:
        yield vertex_index


def colour_polygons(red, green, blue, polygons):
    if polygons:
        cmds.polyColorPerVertex(polygons, colorRGB=[red / 255, green / 255, blue / 255], alpha=1, notUndoable=True, colorDisplayOption=True)


def decolour_polygons(polygons):
    if polygons:
        try:
            cmds.polyColorPerVertex(list(polygons), remove=True)
        except Exception as err:
            print(f"Failed to decolourize polygon(s): {err}")


def remove_all_colours(meshes=None):
    vertex_colours = cmds.ls(type="polyColorPerVertex") or []

    if vertex_colours:
        cmds.delete(vertex_colours)

    for mesh in meshes or []:
        for color_set in cmds.polyColorSet(mesh, query=True, allColorSets=True) or []:
            cmds.polyColorSet(mesh, colorSet=color_set, delete=True)
