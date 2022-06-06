# -*- coding: utf-8 -*-

import requests
import re
import sys
import json


class MunichOnlineAppointments():

	sess = False


	def __init__(self):
		self.sess = requests.session()


	def servicesToCTS(self, services):
		dlListBB = {} #taken from the website
		dlListBB["Abgabe von Fundstücken"] = "1010032"
		dlListBB["Abmeldung (Einzelperson oder Familie)"] = "1064404"
		dlListBB["Adressänderung in Fahrzeugpapiere eintragen lassen"] = "1064129"
		dlListBB["An- oder Ummeldung - Einzelperson mit eigenen Fahrzeugen"] = "1000063"
		dlListBB["An- oder Ummeldung - Einzelperson"] = "1064399"
		dlListBB["An- oder Ummeldung - Familie mit eigenen Fahrzeugen"] = "1000062"
		dlListBB["An- oder Ummeldung - Familie"] = "1000061"
		dlListBB["Ausweisdokumente - Familie (Minderjährige und deren gesetzliche Vertreter)"] = "10225212"
		dlListBB["Antrag oder Verlängerung/Aktualisierung Kinderreisepass"] = "1076792"
		dlListBB["Antrag Personalausweis"] = "1064388"
		dlListBB["Antrag Reisepass/Expressreisepass"] = "1064394"
		dlListBB["Antrag vorläufiger Reisepass"] = "1080586"
		dlListBB["Ausweisdokumente - Familie (Minderjährige und deren gesetzliche Vertreter)"] = "1010012"
		dlListBB["Bis zu 20 Beglaubigungen"] = "1010022"
		dlListBB["Bis zu 5 Beglaubigungen Dokument"] = "1010021"
		dlListBB["Bis zu 5 Beglaubigungen Unterschrift"] = "10100210"
		dlListBB["Eintragung Übermittlungssperre"] = "1064448"
		dlListBB["Eintragung von Änderungen an Personendaten"] = "1010005"
		dlListBB["Fabrikneues Fahrzeug anmelden (mit deutschen Fahrzeugpapieren und CoC)"] = "1064061"
		dlListBB["Fahrzeug außer Betrieb setzen"] = "1064471"
		dlListBB["Fahrzeug umschreiben innerhalb Münchens"] = "1064085"
		dlListBB["Fahrzeug umschreiben von außerhalb nach München"] = "1064322"
		dlListBB["Fahrzeug wieder anmelden"] = "1064477"
		dlListBB["Familienstandsänderung/ Namensänderung"] = "10224134"
		dlListBB["Führungszeugnis beantragen"] = "1064437"
		dlListBB["Gewerbeabmeldung"] = "1010018"
		dlListBB["Gewerbeummeldung (Adressänderung innerhalb Münchens)"] = "10100181"
		dlListBB["Gewerbezentralregisterauskunft beantragen – juristische Person"] = "1010020"
		dlListBB["Gewerbezentralregisterauskunft beantragen – natürliche Person"] = "1064493"
		dlListBB["Haushaltsbescheinigung"] = "1080845"
		dlListBB["Kurzzeitkennzeichen beantragen"] = "1064332"
		dlListBB["Mehr als 20 Beglaubigungen"] = "1010023"
		dlListBB["Meldebescheinigung"] = "1064409"
		dlListBB["Melderegisterauskunft"] = "1064432"
		dlListBB["Nachstempelung Kennzeichen"] = "1010029"
		dlListBB["Nachträgliche Anschriftenänderung Personalausweis/Reisepass/eAT"] = "10184239"
		dlListBB["Nachträgliches Einschalten eID / Nachträgliche Änderung PIN"] = "1010013"
		dlListBB["Namensänderung in Fahrzeugpapiere eintragen lassen"] = "1064138"
		dlListBB["Saisonkennzeichen beantragen"] = "1064341"
		dlListBB["Umweltplakette/ Feinstaubplakette für Umweltzone beantragen"] = "1064443"
		dlListBB["Verlust oder Diebstahl der Zulassungsbescheinigung Teil I"] = "1064499"
		dlListBB["Verlust- oder Diebstahlanzeige von Personalausweis"] = "1076891"
		dlListBB["Verlust- oder Diebstahlanzeige von Reisepass"] = "1078276"
		dlListBB["Widerruf der Verlust- oder Diebstahlanzeige von Personalausweis oder Reisepass"] = "1010016"

		cts = "" #cts=#ID=#COUNT,#ID=#COUNT,...
		for serviceName, serviceCount in services.items():
			if int(serviceCount) <= 0:
				continue

			cts += "{}={},".format(dlListBB[serviceName], serviceCount)

		return cts[:-1]


	def servicesToPayload(self, services):
		payload = {}

		for serviceName, serviceCount in services.items():
			payload["CASETYPES[{}]".format(serviceName)] = serviceCount

		return payload


	def extractAppointments(self, html):
		raw = re.search("var jsonAppoints = '(.+?)';", html).group(1)
		return json.loads(raw)


	def prettyPrintAppointments(self, apts):
		for location, data in apts.items():
			print("Location:", data["caption"])
			for date, times in data["appoints"].items():
				if len(times) > 0:
					print(date, ": ", times)
			print("\n\n")


	def getAppointments(self, services):

		# request base page and get session cookie
		page_base = self.sess.get("https://www.muenchen.de/rathaus/terminvereinbarung_bb.html")

		# extract url from base page
		url = re.search("var url = '(.+?)';", page_base.text).group(1)

		# request page with service selection
		page_services = self.sess.get(url, params={"loc": "BB"})

		payload = self.servicesToPayload(services)
		payload["step"] = "WEB_APPOINT_SEARCH_BY_CASETYPES"


		# get list of possible appointments from outer branches
		page_appointments_branches = self.sess.post(url, params={"loc": "BB"}, data=payload)

		apts = self.extractAppointments(page_appointments_branches.text)
		
		
		# get list of possible appointments from ruppertstr
		cts = self.servicesToCTS(services)

		# for some strange reason this request is necessary, probaply session shenanigans ¯\_(ツ)_/¯
		url = "https://www22.muenchen.de/kvr/termin/"
		self.sess.get(url, params={"cts": cts})

		# get the actual list
		url = "https://www22.muenchen.de/kvr/termin/index.php"
		page_appointments_ruppertstr = self.sess.post(url, params={"cts": cts}, data=payload)

		apts_ruppertstr = self.extractAppointments(page_appointments_ruppertstr.text)

		# append to branches list
		apts["ruppertstr"] = apts_ruppertstr["LOADBALANCER"]

		return apts


if __name__ == "__main__":
	pass
