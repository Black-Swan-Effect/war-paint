#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from maya import cmds


def delete_blendshape(morph_mesh, blendshape):
    if morph_mesh and cmds.getAttr(f"{morph_mesh}.visibility") == 0:
        cmds.showHidden(morph_mesh)

    if cmds.objExists(blendshape):
        cmds.delete(blendshape)


def create_blendshape(base_mesh, morph_mesh, name, alias):
    blendshape = cmds.blendShape(morph_mesh, base_mesh, name=name)[0]
    cmds.aliasAttr(alias, f"{blendshape}.{morph_mesh}")
    cmds.hide(morph_mesh)

    return blendshape


def create_centered_follicle(face, name):
    """Create a centered follicle on a given face.

    Args:
        face (str): the face to create the centered follicle on.
        name (str): the name of give the follicle.

    Returns:
        str: the follicle transform node string."""

    vertex_indices = cmds.filterExpand(cmds.polyListComponentConversion(face, fromFace=True, toVertex=True), selectionMask=31)
    vertex_count, vertex_positions = len(vertex_indices), [cmds.pointPosition(index, world=True) for index in vertex_indices]
    face_center = [sum(coord) / vertex_count for coord in zip(*vertex_positions)]

    face_shape = cmds.listRelatives(face, shapes=True, parent=True)[0]
    closest_point = cmds.createNode("closestPointOnMesh", skipSelect=True)

    # -- Connect Closest Point to Face.
    cmds.connectAttr(f"{face_shape}.outMesh", f"{closest_point}.inMesh")
    cmds.connectAttr(f"{face_shape}.worldMatrix[0]", f"{closest_point}.inputMatrix")
    cmds.setAttr(f"{closest_point}.inPosition", *face_center, type="double3")

    # -- Create Follicle.
    follicle_shape = cmds.createNode("follicle", skipSelect=True, name=f"{name}Shape")
    follicle = cmds.listRelatives(follicle_shape, parent=True)[0]

    cmds.connectAttr(f"{follicle_shape}.outTranslate", f"{follicle}.translate")
    cmds.connectAttr(f"{follicle_shape}.outRotate", f"{follicle}.rotate")

    # -- Connect Follicle to Face.
    cmds.connectAttr(f"{face_shape}.outMesh", f"{follicle_shape}.inputMesh")
    cmds.connectAttr(f"{face_shape}.worldMatrix[0]", f"{follicle_shape}.inputWorldMatrix")

    # -- Set Follicle Position.
    cmds.setAttr(f"{follicle_shape}.parameterU", cmds.getAttr(f"{closest_point}.parameterU"))
    cmds.setAttr(f"{follicle_shape}.parameterV", cmds.getAttr(f"{closest_point}.parameterV"))

    # -- Clean-Up.
    cmds.delete(closest_point)

    return follicle
