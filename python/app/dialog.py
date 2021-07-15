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

        self._types = ('bgeo.sc', 'vdb', 'abc', 'obj', 'usd', 'ass', 'ass.gz')

        self._setup_ui()

    ###################################################################################################
    # UI callbacks

    def _on_btn_press(self):
        name = self._name_line.text()
        name = name.replace(' ', '_')

        if not name.isdigit() and len(hou.selectedNodes()) != 0:
            current_combo = self._type_combo.currentText()
            sim_toggle = self._sim_toggle.isChecked()
            version_toggle = self._version_toggle.isChecked()
            publish_toggle = self._publish_toggle.isChecked()
            frame_range = self._range_combo.currentIndex()
            
            self._on_dialog_close(name, current_combo, sim_toggle, version_toggle, publish_toggle, frame_range)
            self.close()

    def _on_dialog_close(self, name, combo_text, init_sim, auto_version, auto_publish, frame_range):
        # Call back from the Updater Dialog
        # Creates the actual nodes
        node_select = hou.selectedNodes()

        if node_select:
            out = hou.node('/out')

            for node in node_select:
                # Check if node is a sop node
                if node.type().category().name() == 'Sop':
                    # Check for name
                    if name == '':
                        node_name = node.name()
                    else:
                        node_name = name

                    # Create nodes
                    null = node.createOutputNode('null', 'OUT_%s' % (node_name))
                    null.setPosition(node.position())
                    null.move([0, -1])

                    filenode = null.createOutputNode('sgtk_file', node_name)
                    filenode.setPosition(null.position())
                    filenode.move([0, -1])
                    filenode.setColor(hou.Color(0.8, 0.1, 0.1))

                    outnode = out.createNode('sgtk_geometry', node_name)

                    filenode.parm('rop').set(outnode.path())
                    filenode.parm('rop').pressButton()

                    outnode.parm('soppath').set(null.path())
                    outnode.parm('types').set(combo_text)

                    outnode.parm('initsim').set(init_sim)
                    outnode.parm('auto_ver').set(auto_version)
                    outnode.parm('auto_pub').set(auto_publish)
                    outnode.parm('trange').set(frame_range)

                    # trigger refresh of path
                    outnode.parm('types').pressButton()

    ###################################################################################################
    # Private Functions

    def _setup_ui(self):
        self.setWindowTitle('Create Output')
        self.setFixedSize(465, 125)

        output_group = QtGui.QGroupBox('Create Output')
        
        # Name and type layout
        type_layout = QtGui.QHBoxLayout()

        type_label = QtGui.QLabel('Type:')

        self._type_combo = QtGui.QComboBox()
        for out_type in self._types:
            self._type_combo.addItem(out_type)
        
        self._name_line = QtGui.QLineEdit()
        self._name_line.setPlaceholderText('Cache Name')
        self._name_line.returnPressed.connect(self._on_btn_press)

        cache_name = QtGui.QLabel('Cache Name:')

        type_layout.addWidget(type_label)
        type_layout.addWidget(self._type_combo)
        type_layout.addWidget(cache_name)
        type_layout.addWidget(self._name_line)

        # toggles layout
        range_label = QtGui.QLabel('Range:')
        
        self._range_combo = QtGui.QComboBox()
        self._range_combo.addItem('Single')
        self._range_combo.addItem('Multiple')
        self._range_combo.setCurrentIndex(1)

        range_layout = QtGui.QHBoxLayout()
        range_layout.addWidget(range_label)
        range_layout.addWidget(self._range_combo)

        self._sim_toggle = QtGui.QCheckBox('Simulation')
        self._version_toggle = QtGui.QCheckBox('Auto Version')
        self._version_toggle.setChecked(True)
        self._publish_toggle = QtGui.QCheckBox('Auto Publish')
       
        toggle_layout = QtGui.QHBoxLayout()

        toggle_layout.addLayout(range_layout)
        toggle_layout.addWidget(self._sim_toggle)
        toggle_layout.addWidget(self._version_toggle)
        toggle_layout.addWidget(self._publish_toggle)
        
        # Add layout
        changedgroup_layout = QtGui.QVBoxLayout(output_group)
        changedgroup_layout.addLayout(type_layout)
        changedgroup_layout.addLayout(toggle_layout)

        # Create _button
        self._button = QtGui.QPushButton('Create outputs')
        self._button.clicked.connect(self._on_btn_press)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(output_group)
        layout.addWidget(self._button)
        self.setLayout(layout)
