# -*- coding: utf-8 -*-
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

import urllib
import pacparser
import os
import socket
import sys

class proxyList:
    def __init__(self, urlToCheck):
        self.url = urlToCheck
        self.config_dir = os.path.join(os.sys.path[0], 'config')
        pacUrl = self._loadFromFile(self.config_dir, 'pacurl')
        if pacUrl:
            self.proxies = self.getPacConfig(pacUrl)
        else:
            self.proxies = None
    
    def checkProxiesForUrl(self, pac, url):
      """get proxy for the given url"""
      try:
        proxy_string = pacparser.just_find_proxy(pac, url)
      except:
        sys.stderr.write('could not determine proxy using Pacfile\n')
        return None
      proxylist = proxy_string.split(";")
      proxies = None        # Dictionary to be passed to urlopen method of urllib
      while proxylist:
        proxy = proxylist.pop(0).strip()
        if 'DIRECT' in proxy:
          proxies = {}
          return proxies
          #break
        if proxy[0:5].upper() == 'PROXY':
          proxy = proxy[6:].strip()
          if self.isProxyAlive(proxy):
            proxies = {'http': 'http://%s' % proxy}
            return proxies
    
    def getPacConfig(self, url):
        """try to download the PAC file from the url supplied, if it fails use direct"""
        try:
            urllib.urlretrieve(url, self.config_dir + '\\' + 'pac')
            proxy = self.checkProxiesForUrl(self.config_dir + '\\' + 'pac', self.url)
            return proxy
        except IOError:
            proxy = None
            return proxy
    
    def isProxyAlive(self, proxy):
      host_port = proxy.split(":")
      if len(host_port) != 2:
        sys.stderr.write('proxy host is not defined as host:port\n')
        return False
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(10)
      try:
        s.connect((host_port[0], int(host_port[1])))
      except Exception, e:
        sys.stderr.write('proxy %s is not accessible\n' % proxy)
        sys.stderr.write(str(e)+'\n')
        return False
      s.close()
      return True
    
    def _loadFromFile(self, dirname, filename):
        """load pac address from file called pacurl in the config folder. the file should contain just one line with http://host.domain format"""
        path=dirname+'/'+filename
        if os.path.isdir(dirname):
            if os.path.isfile(path):
                try:
                    with open(path, 'r') as file:
                        line = file.readline()
                except:
                    return None
                return line
        else:
            os.makedirs(dirname)
