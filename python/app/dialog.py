# Copyright (c) 2015 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk

from sgtk.platform.qt import QtCore, QtGui

import os
import hou

class AppDialog(QtGui.QWidget):
    @property
    def hide_tk_title_bar(self):
        """
        Tell the system to not show the std toolbar
        """
        return True

    def __init__(self, parent=None):
        # first, call the base class and let it do its thing.
        QtGui.QWidget.__init__(self, parent)

        # most of the useful accessors are available through the Application class instance
        # it is often handy to keep a reference to this. You can get it via the following method:
        self._app = sgtk.platform.current_bundle()

        self._types = ['bgeo.sc', 'vdb', 'abc', 'obj']

        self._setup_ui()

    ###################################################################################################
    # UI callbacks

    def _on_btn_press(self):
        name = self._name_line.text()
        name = name.replace(' ', '_')

        if name and not name.isdigit() and len(hou.selectedNodes()) != 0:
            current_combo = self._type_combo.currentText()
            
            self._on_dialog_close(name, current_combo)
            self.close()

    def _on_dialog_close(self, name, combo_text):
        # Call back from the Updater Dialog
        # Creates the actual nodes
        node_select = hou.selectedNodes()

        if node_select:
            out = hou.node('/out')

            for node in node_select:

                # Check if node is a sop node
                if node.type().category().name() != 'Sop':
                    break
                # Check for name
                if name == '':
                    node_name = node.name()
                else:
                    node_name = name

                # Create nodes
                null = node.createOutputNode('null', 'OUT_%s' % (node_name))
                position = node.position()
                null.setPosition(position)
                null.move([0, -1])

                filenode = null.createOutputNode('sgtk_file', node_name)
                position = null.position()
                filenode.setPosition(position)
                filenode.move([0, -1])
                filenode.setColor(hou.Color(0.8, 0.1, 0.1))

                outnode = out.createNode('sgtk_geometry', node_name)

                # Set Parameters (use .name() to update to latest names of nodes in case houdini changed it)
                rop_path = os.path.join(os.path.dirname(outnode.path()), outnode.name())
                filenode.parm('rop').set(rop_path.replace(os.path.sep, '/'))
                filenode.parm('rop').pressButton()
                
                # set type abc
                if combo_text == 'abc':
                    filenode.parm('isalembic').set(True)

                null_path = os.path.join(os.path.dirname(null.path()), null.name())
                outnode.parm('soppath').set(null_path.replace(os.path.sep, '/'))
                outnode.parm('types').set(combo_text)

    ###################################################################################################
    # Private Functions

    def _setup_ui(self):
        self.setWindowTitle('Create Output')
        self.setFixedSize(465, 100)

        output_group = QtGui.QGroupBox('Create Output')
        
        # Create layout
        type_layout = QtGui.QHBoxLayout()

        type_label = QtGui.QLabel('Type:')

        # Add the different _types
        self._type_combo = QtGui.QComboBox()
        for out_type in self._types:
            self._type_combo.addItem(out_type)
        
        self._name_line = QtGui.QLineEdit()
        self._name_line.setPlaceholderText('Cache name')
        self._name_line.returnPressed.connect(self._on_btn_press)

        cache_name = QtGui.QLabel('Cache name:')

        type_layout.addWidget(type_label)
        type_layout.addWidget(self._type_combo)
        type_layout.addWidget(cache_name)
        type_layout.addWidget(self._name_line)
        
        # Add layout
        changedgroup_layout = QtGui.QVBoxLayout(output_group)
        changedgroup_layout.addLayout(type_layout)

        # Create _button
        self._button = QtGui.QPushButton('Create outputs')
        self._button.clicked.connect(self._on_btn_press)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(output_group)
        layout.addWidget(self._button)
        self.setLayout(layout)

    ###################################################################################################
    # navigation

    def navigate_to_context(self, context):
        """
        Navigates to the given context.

        :param context: The context to navigate to.
        """
        self._fill_treewidget()