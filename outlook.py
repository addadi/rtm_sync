# -*- coding: utf-8 -*-
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

#import time
import datetime

#from rfc3339 import rfc3339

import win32com.client

class OutLook():
    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Connecting to Outlook.\n")
        self.outlook = win32com.client.gencache.EnsureDispatch("Outlook.Application")
        self.ns = self.outlook.GetNamespace("MAPI")
        self.oftasks = self.ns.GetDefaultFolder(win32com.client.constants.olFolderTasks)
        self.data = self.oftasks.Items

    def gettaskslist(self):
        self._tasks = []
        for task in range(len(self.data)):
            self.logger.info("Processing task " + str(task))
            otask = self.data.Item(task+1)
            if otask.Class == win32com.client.constants.olTask:
                newtask = Task(otask)
                self.logger.info("Appending task " + newtask.Subject)
                self._tasks.append(newtask)
        return self._tasks

    def add(self, title):
        new_task = self.outlook.CreateItem(win32com.client.constants.olTaskItem)
        new_task.Subject = title
        new_task.Save()
        return Task(new_task)

    def findTask(self, tid):
        EntryID = tid
        searchstr = '"[EntryID]=' +EntryID + '"'
        found = self.oftasks.Items.Find(searchstr)
        return found

    #def saveTask(self, task):
        #task.Save

    def delete(self, task):
        task._ol_task.otask.Delete()

class Task():
    def __init__(self, otask):
        self.Subject = otask.Subject
        self.EntryID = otask.EntryID
        self.LastModificationTime = otask.LastModificationTime
        self.Status = otask.Status
        self.Body = otask.Body
        self.Categories = otask.Categories
        self.DueDate = otask.DueDate
        self.DateCompleted = otask.DateCompleted
        self.StartDate = otask.StartDate
        self.otask = otask

    def updatedUTC(self):
        offset = datetime.datetime.now() - datetime.datetime.utcnow()
        try:
            return datetime.datetime.strptime(str(self['LastModificationTime']),"%m/%d/%y %H:%M:%S") - offset
        except KeyError:
            return datetime.datetime.strptime(self['updated'],"%Y-%m-%dT%H:%M:%S.%fZ")
  
    def completed(self):
        if self['status'] == "needsAction":
            return False
        elif self['status'] == "completed":
            return True
        else:
            return self['status']
    

def toDateTime(value):
    if value.year == 4501:
        value  = datetime.datetime(2012,1,1,00,00,0)
        return value
    
    value = datetime.datetime(
        year=value.year,
        month=value.month,
        day=value.day,
        hour=value.hour,
        minute=value.minute,
        second=value.second
        )
    return value
