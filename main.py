#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import sys
import time
import smtplib
from datetime import datetime

import config
from MunichOnlineAppointments import MunichOnlineAppointments


class MunichNotify():

	mop = False
	services = {}
	notifyStart = ""
	notifyStop = ""


	def __init__(self, start, stop, services):
		self.mop = MunichOnlineAppointments()
		self.notifyStart = datetime.strptime(start, '%Y-%m-%d')
		self.notifyStop = datetime.strptime(stop, '%Y-%m-%d')
		self.services = services


	def findAppointmentsInRange(self, apts):
		result = ""

		for location, data in apts.items():
			for date, times in data["appoints"].items():
				if len(times) == 0:
					continue

				t = datetime.strptime(date, '%Y-%m-%d')
				if self.notifyStart <= t <= self.notifyStop:
					result += "{}: {}\n".format(date, data["caption"])

		return result


	def sendmail(self, msg):
		header  = 'From: %s\n' % config.fromAddr
		header += 'To: %s\n' % config.toAddr
		header += 'Subject: Appointments in Munich availible!\n\n'
		message = header + msg
		message = message.encode("ascii","ignore")

		server = smtplib.SMTP(config.smtpServer)
		server.starttls()
		server.login(config.smtpUser, config.smtpPassword)
		problems = server.sendmail(config.fromAddr, config.toAddr, message)
		server.quit()


	def run(self):
		apts = self.mop.getAppointments(self.services)
		#self.mop.prettyPrintAppointments(apts)
		aptsInRange = self.findAppointmentsInRange(apts)
		if aptsInRange != "" and config.smtpServer != "":
			self.sendmail(aptsInRange)


if __name__ == "__main__":
	mn = MunichNotify(config.notifyStart, config.notifyStop, config.services)
	mn.run()
