# -*- coding: utf-8 -*-
# Copyright (c) 2009 - Luca Invernizzi <invernizzi.l@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import with_statement

import os
import sys
import subprocess
import pickle
#from xdg.BaseDirectory import xdg_config_home
# If needed, replace with os.sys.path[0]

from pyrtm.rtm import createRTM

from rtmTask import RtmTask
from genericProxy import GenericProxy


class RtmProxy(GenericProxy):

    __OL_STATUSES = [0, 2]

    __RTM_STATUSES = [True,
                      False]

    PUBLIC_KEY = "21bbe22383c856bb9d948002cd5c37cf"
    PRIVATE_KEY = "b9a1a41c893c3cef"

    def __init__(self, logger):
        super(RtmProxy, self).__init__()
        self.token = None
        self.logger = logger
        self._ol_to_rtm_status = dict(zip(self.__OL_STATUSES,
                                            self.__RTM_STATUSES))
        self._ol_to_rtm_status[1] = "1"
        self._rtm_to_ol_status = dict(zip(self.__RTM_STATUSES,
                                            self.__OL_STATUSES))

    def getToken(self):
        """gets a token from file (if a previous sync has been
            performed), or opens a browser to request a new one
            (in which case the function returns true). NOTE: token
            is valid forever """
        if self.token == None:
            self.config_dir = \
                os.path.join(os.sys.path[0], 'config')
            self.token = self._smartLoadFromFile(self.config_dir, 'token')
        if self.token == None:
            self.rtm= createRTM(self.PUBLIC_KEY, self.PRIVATE_KEY)
            os.startfile(self.rtm.getAuthURL())
            raw_input('Please press Enter once you gave access to this application on the RTM page opened on your default browser')
            return False
        return True

    def login(self):
        if hasattr(self, 'rtm'):
            try:
                self.token = self.rtm.getToken()
            except:
                self.token = None
        if(self.getToken() == False):
            return False
        try:
            self.rtm = createRTM(self.PUBLIC_KEY, self.PRIVATE_KEY, \
                                                            self.token)
        except:
            self.token = None
        self._smartSaveToFile(self.config_dir, 'token', self.token)
        #NOTE: a timeline is an undo list for RTM. It can be used for
        # journaling(timeline rollback is atomical)
        self.timeline = self.rtm.timelines.create().timeline
        return True

    def downloadFromWeb(self):
        #NOTE: syncing only incomplete tasks for now
        #(it's easier to debug the things you see)
#        lists_id_list = map(lambda x: x.id, \
#                             self.rtm.lists.getList().lists.list)
#	we ignore the All Tasks smart list so that later we won't try to save the a task to a smart list instead of the actual list it belongs in RTM
#perhaps there a smarter way to filter it in RTM api, like with tasks status
#	i've also using a for in loop instead of the original lambda
        lists_id_list = []
        x=self.rtm.lists.getList().lists.list
	for i in x:
		if i.name != u'All Tasks':
			lists_id_list.append(i.id)

        # Download all non-archived tasks in the list with id x
        def get_list_of_taskseries(x):
            #currentlist = self.rtm.tasks.getList(list_id = x, \
                                #filter = 'includeArchived:false').tasks
            currentlist = self.rtm.tasks.getList(list_id = x).tasks
            if hasattr(currentlist, 'list'):
                return currentlist.list
            else:
                return []
        #Workaround for changed RTM api
        task_list_global= map(lambda item: item[0] if type(item) == list and len(item) >= 1 else item,
                              map(get_list_of_taskseries, lists_id_list))
        ###
        taskseries_list = filter(lambda x: hasattr(x[0], 'taskseries'), \
                                  zip(task_list_global, lists_id_list))
        tasks_list_wrapped = map(lambda x: (x[0].taskseries, x[1]), \
                                 taskseries_list)
        tasks_list_normalized = map(lambda x: zip(x[0], [x[1]] * len(x[0]), \
                map(lambda x: x.id, x[0])) if type(x[0]) == list \
                else [(x[0], x[1], x[0].id)], tasks_list_wrapped)
        tasks_list_unwrapped = []
        task_objects_list = []
        list_ids_list = []
        taskseries_ids_list = []
        if len(tasks_list_normalized)>0:
            tasks_list_unwrapped = reduce(lambda x, y: x+y, \
                                          tasks_list_normalized)
            task_objects_list, list_ids_list, taskseries_ids_list = \
                    self._unziplist(tasks_list_unwrapped)

        return zip(task_objects_list, list_ids_list, taskseries_ids_list)

    def generateTaskList(self):
        self._task_list = []
        data = self.downloadFromWeb()
        for task, list_id, taskseries_id in data:
            self._task_list.append(RtmTask(task, list_id, taskseries_id, \
                                          self.rtm, self.timeline, \
                                          self.logger, self))
        if self.logger:
            #map(lambda task: self.logger.debug("RTM task: |" + task.title),
            #                                   self._task_list)
            pass

    def create_new_task(self, title):
        result = self.rtm.tasks.add(timeline=self.timeline, name=title)
        new_task= RtmTask(result.list.taskseries.task, result.list.id,\
                          result.list.taskseries.id, self.rtm, self.timeline,\
                         self.logger, self)
        self._task_list.append(new_task)
        return new_task

    def get_tasks_list(self):
        return self._task_list

    def delete_task(self, task):
        self._task_list.remove(task)
        task.delete()

    def _smartLoadFromFile(self, dirname, filename):
        path=dirname+'/'+filename
        if os.path.isdir(dirname):
            if os.path.isfile(path):
                try:
                    with open(path, 'r') as file:
                        item = pickle.load(file)
                except:
                    return None
                return item
        else:
            os.makedirs(dirname)

    def _smartSaveToFile(self, dirname, filename, item, **kwargs):
        path=dirname+'/'+filename
        try:
            with open(path, 'wb') as file:
                pickle.dump(item, file)
        except:
            if kwargs.get('critical', False):
                raise Exception(_("saving critical object failed"))

    def _unziplist(self, a):
        if len(a) == 0:
            return [], []
        return tuple(map(list, zip(*a)))
