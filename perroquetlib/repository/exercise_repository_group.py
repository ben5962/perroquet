#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2009-2011 Frédéric Bertolus.
# Copyright (C) 2009-2011 Matthieu Bizien.
#
# This file is part of Perroquet.
#
# Perroquet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Perroquet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Perroquet.  If not, see <http://www.gnu.org/licenses/>.

import errno
import os
from xml.dom.minidom import getDOMImplementation, parse

from perroquetlib.repository.exercise_repository_exercise import ExerciseRepositoryExercise

class ExerciseRepositoryGroup:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.exercisesList = []

        self.system = False



    def set_system(self, system):
        """Define if the group is a system repository or only a local one

        A system group store common data in a system directory and only the
        progress in the local directory
        """
        self.system = system;


    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def add_exercise(self, exercise):
        self.exercisesList.append(exercise)
        exercise.set_parent(self)

    def get_exercises(self):
        return self.exercisesList

    def set_parent(self, parent):
        self.parent = parent

    def get_local_path(self):
            return os.path.join(self.parent.get_local_path(), self.id)

    def get_personal_local_path(self):
            return os.path.join(self.parent.get_personal_local_path(), self.id)


    def parse_description(self, xml_group):
        self.set_name(self._get_text(xml_group.getElementsByTagName("name")[0].childNodes))
        self.set_id(self._get_text(xml_group.getElementsByTagName("id")[0].childNodes))
        self.set_description(self._get_text(xml_group.getElementsByTagName("description")[0].childNodes))

    def generate_description(self):
        self._generate_description()
        for exo in self.get_exercises():
            exo.generate_description()

    def _generate_description(self):

        if not os.path.isdir(self.get_local_path()):
            try:
                os.makedirs(self.get_local_path())
            except OSError, (ErrorNumber, ErrorMessage): # Python <=2.5
                if ErrorNumber == errno.EEXIST:
                    pass
                else: raise

        impl = getDOMImplementation()

        newdoc = impl.createDocument(None, "perroquet_group", None)
        root_element = newdoc.documentElement

        # Name
        xml_name = newdoc.createElement("name")
        xml_name.appendChild(newdoc.createTextNode(self.get_name()))
        root_element.appendChild(xml_name)

        # Id
        xml_id = newdoc.createElement("id")
        xml_id.appendChild(newdoc.createTextNode(self.get_id()))
        root_element.appendChild(xml_id)

        # Description
        xml_description = newdoc.createElement("description")
        xml_description.appendChild(newdoc.createTextNode(self.get_description()))
        root_element.appendChild(xml_description)

        xml_string = newdoc.toprettyxml()
        xml_string = xml_string.encode('utf8')

        repoDescriptionPath = os.path.join(self.get_local_path(), "group.xml")
        f = open(repoDescriptionPath, 'w')
        f.write(xml_string)
        f.close()

    def init_from_path(self, groupPath):
        groupDescriptionPath = os.path.join(groupPath, "group.xml")

        # Read group infos from xml description file
        if os.path.isfile(groupDescriptionPath):
            f = open(groupDescriptionPath, 'r')
            dom = parse(f)
            self.parse_description(dom)
        else:
            self.set_id(os.path.basename(groupPath))
            self.set_name(os.path.basename(groupPath))

        exercisePathList = os.listdir(groupPath)
        for exercisePath in exercisePathList:
            path = os.path.join(groupPath, exercisePath)
            if os.path.isdir(path):
                exo = ExerciseRepositoryExercise()
                exo.set_system(self.system)
                exo.init_from_path(path)
                self.add_exercise(exo)


    def _get_text(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        rc = rc.strip()
        return rc
