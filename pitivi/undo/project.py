# Pitivi video editor
#
#       pitivi/undo/project.py
#
# Copyright (c) 2012, Thibault Saunier <tsaunier@gnome.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.
from gi.repository import GObject
from gi.repository import Gst

from pitivi.undo.undo import UndoableAction


class AssetAddedAction(UndoableAction):

    def __init__(self, project, asset):
        UndoableAction.__init__(self)
        self.project = project
        self.asset = asset

    def undo(self):
        self.project.remove_asset(self.asset)

    def do(self):
        self.project.add_asset(self.asset)

    def asScenarioAction(self):
        st = Gst.Structure.new_empty("add-asset")
        st.set_value("id", self.asset.get_id())
        type_string = GObject.type_name(self.asset.get_extractable_type())
        st.set_value("type", type_string)
        return st


class AssetRemovedAction(UndoableAction):

    def __init__(self, project, asset):
        UndoableAction.__init__(self)
        self.project = project
        self.asset = asset

    def undo(self):
        self.project.add_asset(self.asset)

    def do(self):
        self.project.remove_asset(self.asset)

    def asScenarioAction(self):
        st = Gst.Structure.new_empty("remove-asset")
        st.set_value("id", self.asset.get_id())
        type_string = GObject.type_name(self.asset.get_extractable_type())
        st.set_value("type", type_string)
        return st


class ProjectSettingsChanged(UndoableAction):

    def __init__(self, project, old, new):
        UndoableAction.__init__(self)
        self.project = project
        self.oldsettings = old
        self.newsettings = new

    def do(self):
        self.project.setSettings(self.newsettings)
        self._done()

    def undo(self):
        self.project.setSettings(self.oldsettings)
        self._undone()


class ProjectObserver():
    """Monitors a project instance and reports UndoableActions.

    Attributes:
        log (UndoableActionLog): The action log where to report actions.
    """

    def __init__(self, log):
        self.log = log

    def startObserving(self, project):
        """Starts monitoring the specified Project.

        Args:
            project (Project): The project to be monitored.
        """
        project.connect("notify-meta", self._settingsChangedCb)
        project.connect("asset-added", self._assetAddedCb)
        project.connect("asset-removed", self._assetRemovedCb)

    def _settingsChangedCb(self, project, item, value):
        """
        FIXME Renable undo/redo
        action = ProjectSettingsChanged(project, old, new)
        self.log.begin("change project settings")
        self.log.push(action)
        self.log.commit()
        """
        pass

    def _assetAddedCb(self, project, asset):
        action = AssetAddedAction(project, asset)
        self.log.push(action)

    def _assetRemovedCb(self, project, asset):
        action = AssetRemovedAction(project, asset)
        self.log.push(action)