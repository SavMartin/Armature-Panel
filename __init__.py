# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {'name': 'Armature Panel',
           'author': 'PΓOXΞ',
           'version': (0, 5),
           'blender': (2, 80, 0),
           'location': '3D View → Properties Panel',
           'description': "Provides a panel that allows quick access to commonl"
                            "y used armature settings within the 3D View.",
           'category': 'Rigging'}

#############
## IMPORTS ##
#############
import bpy
from bpy.types import Operator, PropertyGroup, Menu, Panel
from bpy.props import *
    # PEP8 Compliant


###############
## FUNCTIONS ##
###############
# ##### OPERATOR FUNCTIONS #####

# Shape to bone function.
def shapeToBone(self, context):
    """
    Takes the custom shape assigned to the active pose bone and aligns it to the
    pose bone's orientation.
    """
    
    # Main variables.
    shapeToBoneOptions = context.window_manager.shapeToBoneSettings
    activeArmature = context.active_object
    activeBone = context.active_bone
    activePoseBone = activeArmature.pose.bones[activeBone.name]
    shape = activePoseBone.custom_shape
    shapeTransform = activePoseBone.custom_shape_transform
    
    # Custom shape transform.
    if shapeTransform:
        targetMatrix = (activeArmature.matrix_world @ shapeTransform.matrix)
    else:
        targetMatrix = (activeArmature.matrix_world @ activeBone.matrix_local)
    
    # Location, rotation, scale.
    shape.location = targetMatrix.to_translation()
    shape.rotation_mode = 'XYZ'
    shape.rotation_euler = targetMatrix.to_euler()
    targetScale = targetMatrix.to_scale()
    scaleAverage = ((targetScale[0] + targetScale[1] + targetScale[2]) / 3)
    shape.scale = ((activeBone.length * scaleAverage),
                   (activeBone.length * scaleAverage),
                   (activeBone.length * scaleAverage))
    
    #Draw options.
    if shapeToBoneOptions.showWire:
        activeBone.show_wire = True
    if shapeToBoneOptions.wireDrawType:
        shape.display_type = 'WIRE'
    
    # Datablock name.
    if shapeToBoneOptions.nameShape:
        targetName = activeBone.name
        if shapeToBoneOptions.includeArmatureName:
            targetName = (activeArmature.name +
                    shapeToBoneOptions.separateArmatureName +
                    targetName)
        shape.name = (shapeToBoneOptions.prefixShapeName + targetName)
        if shapeToBoneOptions.prefixShapeDataName:
            shape.data.name = (shapeToBoneOptions.prefixShapeName + targetName)
        else:
            shape.data.name = targetName


#############
## CLASSES ##
#############
# ##### PROPERTY GROUP CLASSES #####

# Shape to bone property group class.
class shapeToBonePropertyGroup(bpy.types.PropertyGroup):
    """
    Property group; space_view3d_armature.py
    Properties for shapeToBoneOperator class that effect how it will proceed.
    """
    # Show wire.
    showWire : BoolProperty(name='Draw Wire', description="Turn on the bones dr"
                            "aw wire option when the shape is aligned to the bo"
                            "ne (Bone is always drawn as a wire-frame regardles"
                            "s of the view-port draw mode.)", default=True)
    # Wire draw type.
    wireDrawType : BoolProperty(name='Wire Draw Type', description="Change the "
                                "custom shape object draw type to wire, when th"
                                "e shape is aligned to the bone.",
                                default=True)
    # Name shape.
    nameShape : BoolProperty(name='Auto-Name', description="Automatically name "
                                "and prefix the custom shape based on the bone it "
                                "is assigned to.", default=True)
    # Prefix shape name.
    prefixShapeName : StringProperty(name='Prefix', description="Use this prefi"
                                        "x when naming a custom bone shape. (Leave"
                                        " blank if you do not wish to prefix the n"
                                        "ame.)", default='')
    # Prefix shape data name.
    prefixShapeDataName : BoolProperty(name='Prefix Shape Data Name',
                                        description="Prefix the custom shape's o"
                                        "bject data name in addition to prefixin"
                                        "g the custom shapes name.",
                                        default=False)
    # Include armature name.
    includeArmatureName : BoolProperty(name='Include Armature Name',
                                        description="Include the armature name w"
                                        "hen renaming the custom shape.",
                                        default=False)
    # Seperate armature name.
    separateArmatureName : StringProperty(name='Separator', description="Separa"
                                            "te the name of the armature and the "
                                            "name of the bone with this character"
                                            ".", default='-')


# Armature panel property group class.
class armaturePanelPropertyGroup(bpy.types.PropertyGroup):
    """
    Property Group; space_view3d_armature.py
    Properties for armaturePanel class that effect how it is displayed.
    """
    # Context options.
    contextOptions = [('ARMATURE', 'Armature Options', "Display options that pu"
                        "rtain to the properties window armature context.", 'ARM'
                        'ATURE_DATA', 0),
                        ('BONE', 'Bone Options', "Display options that purtain to"
                        " the properties window bone context", 'BONE_DATA', 1),
                        ('BONE_CONSTRAINT', 'Bone Constraint Options', "Display o"
                        "ptions that purtain to the properties window bone const"
                        "raint context.", 'CONSTRAINT_BONE', 2),
                        ('SHAPE_TO_BONE', 'Shape to Bone', "Display options that "
                        "purtain to the operator; 'Shape to Bone'", 'AUTO', 3)]
    # Display context.
    displayContext : EnumProperty(name='Display Context', description="Type of context to display in this panel.",items=contextOptions, default='ARMATURE')

# ##### OPERATOR CLASSES #####

# Shape to bone operator class.
class shapeToBoneOperator(bpy.types.Operator):
    """
    Align currently assigned custom bone shape on a visible scene layer to
    active pose bone.
    """
    # Main variables.
    bl_idname = 'pose.shape_to_bone'
    bl_label = 'Align to Bone'
    bl_description = ("Align currently assigned custom bone shape on a visible scene layer to active pose bone.")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    # Poll.
    def poll(cls, context):
        """ poll; context.active_bone and mode == 'POSE'. """
        return context.active_bone and context.mode == 'POSE'
    
    # Draw.
    def draw(self, context):        
        """ Draw the shapleToBone settings. """
        shapeToBoneOptions = context.window_manager.shapeToBoneSettings
        layout = self.layout
        column = layout.column(align=True)
        column.prop(shapeToBoneOptions, 'showWire')
        column.prop(shapeToBoneOptions, 'wireDrawType')
        column.prop(shapeToBoneOptions, 'nameShape')
        column.prop(shapeToBoneOptions, 'prefixShapeName', text="Prefix:")
        column.prop(shapeToBoneOptions, 'prefixShapeDataName')
        column.prop(shapeToBoneOptions, 'includeArmatureName')
        column.prop(shapeToBoneOptions, 'separateArmatureName')
    
    # Execute.
    def execute(self, context):
        """ Execute shapeToBone """
        shapeToBone(self, context)
        return {'FINISHED'}

# ##### INTERFACE CLASSES #####

    # Armature panel class.
class ARMATURE_PT_armaturePanel(bpy.types.Panel):
    """
    Armature panel for the add-on; space_view3d_armature.py
    This panel is located in the 3D view's properties window, while in pose or
    armature edit mode, decided to go with a unique design here.
    """
    # Main variables.
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Armature'
    bl_category = "Armature"
    
    # Poll.
    @classmethod
    def poll(cls, context):
        """ poll; context.mode in {'POSE', 'EDIT_ARMATURE'}. """
        return context.mode in {'POSE', 'EDIT_ARMATURE'}
    
    # Draw.
    def draw(self, context):
        
        # Main variables.
        armaturePanelOptions = context.window_manager.armaturePanelSettings
        object = context.object
        armature = bpy.data.armatures[object.name]
        bone = context.active_bone
        poseBone = object.pose.bones[bone.name]
        bone_list = "bones"
        arm = bpy.data.armatures
        
        # Layout
        layout = self.layout
        column = layout.column(align=True)
        
        # Display options.
        columnRow = column.row()
        columnRow.prop(armaturePanelOptions, 'displayContext', text="",expand=True)

        # Armature options.
        if armaturePanelOptions.displayContext == 'ARMATURE':
            column.separator()
            column.template_ID(object, 'data')
            column.separator()
            column.label(text="Skeleton:")
            column.separator()
            if context.mode == 'POSE':
                columnRow = column.row()
                columnRow.prop(armature, 'pose_position', text="")
                column.separator()
            column.prop(armature, 'layers', text="")
            column.separator()
            column.label(text="Display :")
            column.separator()
            column.prop(armature, 'display_type', text="")
            columnSplit = column.split(align=True)
            columnSplit.prop(armature, 'show_names', text="Names",toggle=True)
            columnSplit.prop(armature, 'show_group_colors', text="Colors",toggle=True)
            columnSplit = column.split(align=True)
            columnSplit.prop(armature, 'show_axes', text="Axes",toggle=True)
            if object:
                columnSplit.prop(object, 'show_in_front', text="In Front",toggle=True)

            columnSplit = column.split(align=True)
            columnSplit.prop(armature, 'show_bone_custom_shapes',text="Shapes", toggle=True)

            # Bone groups
            boneGroups = object.pose.bone_groups.active
            column.separator()
            column.label(text="Bone Groups:")
            column.separator()
            if boneGroups:
                rowCount = 4
            else:
                rowCount = 1
            columnRow = column.row()
            columnRow.template_list('UI_UL_list', 'bone_groups',
                                    object.pose, 'bone_groups',
                                    object.pose.bone_groups,
                                    'active_index', rows=rowCount)
            rowColumn = columnRow.column(align=True)
            rowColumn.active = object.proxy is None
            rowColumn.operator('pose.group_add', icon='ADD', text="")
            rowColumn.operator('pose.group_remove', icon='REMOVE', text="")
            rowColumn.menu('DATA_MT_bone_group_context_menu',icon='DOWNARROW_HLT', text="") #sav
            if boneGroups:
                rowColumn.separator()
                rowColumn.operator('pose.group_move', icon='TRIA_UP',text="").direction = 'UP'
                rowColumn.operator('pose.group_move', icon='TRIA_DOWN',text="").direction = 'DOWN'
                rowColumn.separator()
                columnSplit.active = object.proxy is None
                columnSplit = column.split()
                columnSplit.prop(boneGroups, 'color_set', text="")
                if boneGroups.color_set:
                    subSplit = columnSplit.split(align=True)
                    subSplit.prop(boneGroups.colors, 'normal', text="")
                    subSplit.prop(boneGroups.colors, 'select', text="")
                    subSplit.prop(boneGroups.colors, 'active', text="")
            column.separator()
            columnRow = column.row()
            columnRow.active = object.proxy is None
            subRow = columnRow.row(align=True)
            subRow.operator('pose.group_assign', text="Assign")
            subRow.operator('pose.group_unassign', text="Remove")
            subRow = columnRow.row(align=True)
            subRow.operator('pose.group_select', text="Select")
            subRow.operator('pose.group_deselect', text="Deselect")

            # Pose library.
            poseLibrary = object.pose_library
            column.separator()
            column.label(text="Pose Library:")
            column.separator()
            columnRow = column.row()
            column.separator()
            columnRow.template_ID(object, 'pose_library', new='poselib.new',unlink='poselib.unlink')
            if poseLibrary:
                columnRow = column.row()
                columnRow.template_list('UI_UL_list', 'pose_markers',
                                        poseLibrary, 'pose_markers',
                                        poseLibrary.pose_markers, 'active_i'
                                        'ndex', rows=3)
                rowColumn = columnRow.column(align=True)
                rowColumn.active = poseLibrary.library is None
                rowColumn.operator('poselib.pose_add', icon='ZOOM_IN',text="")
                rowColumn.operator_context = 'EXEC_DEFAULT'
                poseMarkerActive = poseLibrary.pose_markers.active
                if poseMarkerActive:
                    rowColumn.operator('poselib.pose_remove',icon='ZOOM_OUT', text="")
                    activeIndex = poseLibrary.pose_markers.active_index
                    rowColumn.operator('poselib.apply_pose', icon='ZOOM_SELECTED',text="").pose_index = activeIndex
                rowColumn.operator('poselib.action_sanitize', icon='HELP',text="")
        
        # Bone options.
        if armaturePanelOptions.displayContext == 'BONE':
            column.separator()
            columnRow = column.row()
            subRow = columnRow.row()
            subRow.label(text="", icon='BONE_DATA')
            columnRow.prop(bone, 'name', text="")
            column.separator()
        
            # Relations
            column.label(text="Relations:")
            column.separator()
            column.prop(bone, 'layers', text="")
            column.separator()
            if context.mode == 'POSE':
                column.prop_search(poseBone, 'bone_group', object.pose,'bone_groups', text="")
                column.prop(bone, 'use_relative_parent', toggle=True)
            column.prop(bone, 'parent', text="")
            subColumn = column.column(align=True)
            subColumn.active = bone.parent is not None
            subColumn.prop(bone, 'use_connect', toggle=True)
            columnSplit = column.split(align=True)
            columnSplit.active = bone.parent is not None
            columnSplit.prop(bone, 'use_inherit_rotation', toggle=True)
            columnSplit.prop(bone, 'use_inherit_scale', toggle=True)
            subColumn = column.column(align=True)
            subColumn.active = not bone.parent or not bone.use_connect
            subColumn.prop(bone, 'use_local_location', toggle=True)
            column.separator()
            
            # Deform
            column.prop(bone, 'use_deform', text="Deform:")
            column.separator()
            column = column.column(align=True)
            column.active = bone.use_deform
            column.prop(bone, 'use_envelope_multiply', text="Multiply",
                        toggle=True)
            column.prop(bone, 'envelope_distance', text="Distance")
            column.prop(bone, 'envelope_weight', text="Weight")
            column.separator()
            column.prop(bone, 'head_radius', text="Head")
            column.prop(bone, 'tail_radius', text="Tail")
            column.separator()
            column.prop(bone, 'bbone_segments', text="Segments")
            column.prop(bone, 'bbone_easein', text="Ease In")
            column.prop(bone, 'bbone_easeout', text="Ease Out")
            if context.mode == 'POSE':
                column.prop(bone, 'bbone_handle_type_start', text="Start Handle")
                column.prop_search(bone, "bbone_custom_handle_start", armature, bone_list, text="Custom")
                column.prop(bone, 'bbone_handle_type_end', text="End Handle")
                column.prop_search(bone, "bbone_custom_handle_end", armature, bone_list, text="Custom")
        # Bone constraint options.
        if armaturePanelOptions.displayContext == 'BONE_CONSTRAINT':
            if context.mode == 'POSE':
                column.separator()
                column.operator_menu_enum('pose.constraint_add', 'type',text="Add Bone Constraint")
                for constraint in poseBone.constraints:
                    column.separator()
                    columnRow = column.row(align=True)
                    columnRow.prop(constraint, 'show_expanded', text="")
                    columnRow.prop(constraint, 'name', text="")
                    if constraint.mute:
                        muteIcon = 'RESTRICT_VIEW_ON'
                    else:
                        muteIcon = 'RESTRICT_VIEW_OFF'
                    columnRow.prop(constraint, 'mute', text="",icon=muteIcon)
                    columnRow.operator('constraint.move_up', text="",icon='TRIA_UP')
                    columnRow.operator('constraint.move_down', text="",icon='TRIA_DOWN')
                    columnRow.operator('constraint.delete', text="",icon='X')
                    if constraint.show_expanded:
                        column.prop(constraint, 'target', text="")
                        if constraint.target:
                            if constraint.target.type == 'ARMATURE':
                                column.prop_search(constraint, 'subtarget',constraint.target.data,'bones', text="")
                        column.prop(constraint, 'influence')
            else:
                column.separator()
                column.label(text="Must be in pose mode.")

        # Shape to bone options.
        if armaturePanelOptions.displayContext == 'SHAPE_TO_BONE':
            if context.mode == 'POSE':
                column.separator()
                subColumn = column.column(align=True)
                subColumn.active = bool(poseBone.custom_shape)
                subColumn.scale_y = 1.5
                subColumn.operator('pose.shape_to_bone', text="Align Custom Shape")
                column.separator()
                
                # Display
                column.label(text="Display:")
                column.separator()
                column.prop(poseBone, 'custom_shape', text="")
                if poseBone.custom_shape:
                    column.prop_search(poseBone, 'custom_shape_transform',object.pose, 'bones', text="")
                columnSplit = column.split(align=True)
                columnSplit.prop(bone, 'hide', text="Hide", toggle=True)
                columnSplitRow = columnSplit.row(align=True)
                columnSplitRow.active = bool(poseBone.custom_shape)
                columnSplitRow.prop(bone, 'show_wire', text="Wireframe", toggle=True)
            else:
                column.separator()
                column.label(text="Must be in pose mode.")


# ##### REGISTER FUNCTIONS #####

# Register function.

def register():
    bpy.utils.register_class(ARMATURE_PT_armaturePanel)
    bpy.utils.register_class(shapeToBoneOperator)
    bpy.utils.register_class(shapeToBonePropertyGroup)
    bpy.utils.register_class(armaturePanelPropertyGroup)

    shapeToBoneProperties = bpy.props.PointerProperty(type=shapeToBonePropertyGroup)
    armaturePanelProperties = bpy.props.PointerProperty(type=armaturePanelPropertyGroup)
    shapeToBoneProperties = bpy.props.PointerProperty(type=shapeToBonePropertyGroup)

    windowManager = bpy.types.WindowManager
    windowManager.armaturePanelSettings = armaturePanelProperties
    windowManager.shapeToBoneSettings = shapeToBoneProperties

# Assign names for completeness.
    bpy.context.window_manager.armaturePanelSettings.name = 'Armature Panel'
    bpy.context.window_manager.shapeToBoneSettings.name = 'Shape to Bone'



# Unregister function.

def unregister():
    """ Unregister """
    bpy.utils.unregister_class(ARMATURE_PT_armaturePanel)
    bpy.utils.unregister_class(shapeToBoneOperator)
    bpy.utils.unregister_class(shapeToBonePropertyGroup)
    bpy.utils.unregister_class(armaturePanelPropertyGroup)

    # Main variables.
    windowManager = bpy.types.WindowManager

    # Delete window manager's property group references.
    try:
        del windowManager.armaturePanelSettings
        del windowManager.shapeToBoneSettings
    except:
        pass

if __name__ == "__main__":
    register()