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

import time
import datetime
import pywintypes
from genericTask import GenericTask

class OlTask(GenericTask):

    def __init__(self, ol_task, ol_proxy):
        super(OlTask, self).__init__(ol_proxy)
        self._ol_task = ol_task

    def _get_title(self):
        return self._ol_task.Subject

    def _set_title(self, title):
        self._ol_task.otask.Subject = title
        self._ol_task.otask.Save 

    def _get_id(self):
        return self._ol_task.EntryID

    def _get_tags(self):
        tags = self._ol_task.Categories
        if tags is not u'':
            return self._ol_task.Categories.split(',')
        else:
            return []

    def _set_tags(self, tags):
        tagstxt = ','.join(tags)
        self._ol_task.otask.Categories = tagstxt
        self._ol_task.otask.Save

    def _get_text(self):
        return self._ol_task.Body

    def _set_text(self, text):
        self._ol_task.otask.Body = text
        #self._ol_task.otask.Save()
        self._ol_task.otask.Save

    def _set_status(self, status):
        self._ol_task.otask.Status = status
        self._ol_task.otask.Save

    def _get_status(self):
        return self._ol_task.Status

    def _get_due_date(self):
        due_date = self._ol_task.DueDate
        if due_date == None or due_date == "" or due_date.year > 2036:
        #if due_date == None or due_date == "":
            return datetime.datetime(2036, 1, 1, 00, 00, 0)
            #return None
        else:
            return self.__time_pytime_to_datetime(due_date)

    def _set_due_date(self, due):
        if due == None or due == "" or due.year > 2036:
        #if due == None or due == "":
            ol_due = datetime.datetime(2036, 1, 1, 00, 00, 0)
            #ol_due = None
            self._ol_task.DueDate = ol_due
            self._ol_task.otask.Save
        else:
            ol_due = self.__time_datetime_to_pytime(due)
            self._ol_task.DueDate = ol_due
            self._ol_task.otask.Save

    def _get_modified(self):
        modified = self._ol_task.LastModificationTime
        if modified == None or modified == "" or modified.year == 4051:
            return None
        return self.__time_pytime_to_datetime(modified)

    def get_ol_task(self):
        return self._ol_task

    def __time_pytime_to_datetime(self, value):
        value = datetime.datetime(
            year=value.year,
            month=value.month,
            day=value.day,
            hour=value.hour,
            minute=value.minute,
            second=value.second
            )
        return value

    def __time_datetime_to_pytime(self, dt_time):
        pyt_time = pywintypes.Time(int(time.mktime(dt_time.timetuple())))
        return pyt_time
