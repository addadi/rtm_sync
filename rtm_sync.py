# -*- coding: utf-8 -*-
# Copyright (c) 2009 - Luca Invernizzi <invernizzi.l@gmail.com>
#                    - Paulo Cabido <paulo.cabido@gmail.com> (example file)
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

#import os
#from threading import Thread
from syncEngine import SyncEngine
#import glob
import logging
import logging.handlers

LOG_FILENAME = 'rtm.log'

class RtmSync:
    #worker_thread = None
    sync_engine = None
    status = None

    def __init__(self, logger=None):
        self.logger = logger
        self.activate()
        self.checkLogin(logger)

    def activate(self):
        self.sync_engine = SyncEngine(self, self.logger)

    def lauchSynchronization(self):
        self.logger.info("Synchronization started \n")
        self.sync_engine.synchronize()

    def checkLogin(self, firstime = True):
        self.firstime = firstime
        self.logger.info("Trying to access, please stand by...")
        try:
            self.sync_engine.rtmLogin()
        except:
            pass
        if self.sync_engine.rtmLogin():
            self.loginHasFailed()
        else:
            self.checkHasLogon()

    def loginHasFailed(self):
        self.logger.info("Couldn't connect to Remember The Milk \n")

    def checkLoginThread(self):
        try:
            self.sync_engine.rtmLogin()
        except:
            pass

    def checkHasLogon(self):
        login = self.sync_engine.rtmHasLogon()
        if login == False:
            if not self.firstime:
                self.logger.info("Authentication failed. Please retry. \n")
            else:
                self.logger.info("Please authenticate to Remember \
The Milk in the browser that is being opened now. \
When done, press OK")
        else:
            self.lauchSynchronization()

    def onTaskOpened(self, plugin_api):
        pass

def main():
    """init logging system, start rtmsync"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(LOG_FILENAME)
    fh.setLevel(logging.INFO)
    #ch = logging.StreamHandler()
    #ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s")
    fh.setFormatter(formatter)
    #ch.setFormatter(formatter)
    logger.addHandler(fh)
    #logger.addHandler(ch)
    r = RtmSync(logger=logger)

if __name__ == "__main__":
    main()
