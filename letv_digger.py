#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2014/1/20 lwldcr@gmail.com

###################################
# for downloading letv.com videos #
###################################

import os,sys
import re,urllib

class Letv(object):
	def __init__(self, url=''):
		self.url = url
		self.vurl = ''

	def fetchHtml(self):
		hs = urllib.urlopen(self.url)
		self.html = hs.read()
		hs.close()
		try:
			self.html = self.html.decode('gbk','ignore')
		except:
			self.html = self.html.decode('utf-8','ignore')
		assert self.html, "fetching page:\"%s\" failed!" % (self.url)
		return True

	def parseVid(self):
		self.vid = re.search(r'vid\:(\d+)\,', self.html).group(1)
		self.title = re.search(r'title\:\"(.*?)\"\,', self.html).group(1)
		return True

	def parseXml(self):
		xmlAdd = 'http://www.letv.com/v_xml/' + self.vid + '.xml'
		res = [ r'1080p',r'720p',r'1300',r'1000',r'350', ]
		xms = urllib.urlopen(xmlAdd)
		self.html = xms.read()
		try:
			self.html = self.html.decode('utf-8')
		except:
			pass
		assert self.html, "fetching page:\"%s\" failed!" % (xmlAdd)

		pattern = r'\:.*?\[\"(http.*?)\"\,.*?\,\"(.*?.flv)\"'
		for r in res:
			pattern = r'\"' + r + r'\"' + pattern
			try:
				ks = re.search(pattern, self.html, re.S)
				part1 = ks.group(1)
				part2 = ks.group(2)
				self.vurl = str(part1 + part2).replace('\\','')
				return True
			except:
				return False

	def download(self):
		try:
			print "Start downloading \"%s\"... " % (self.title)
			urllib.urlretrieve(self.vurl, self.title, cbk)
			print "File \"%s\" downloaded successfully!" % (self.title)
		except KeyboardInterrupt:
			print "\nManually interrupted!"
			print "Deleting temp files...",
			os.remove(self.title)
			print "done!"
			sys.exit(1)
		return True
		
	def parse(self):
		if self.fetchHtml():
			self.parseVid()
			self.parseXml()
		if self.vurl:
			self.download()

class Printer():
    # 单行现实动态信息
    def __init__(self,data):
        sys.stdout.write("\r\x1b[K" + data.__str__())
        sys.stdout.flush()

def cbk(a, b, c):
	"""Callback function for urllib.urlretrieve()."""
	per = 100.0 * a * b / c
	if per > 100:
		per = 100
	text = '-------Completed percentage: %s / %s MB--%.2f%%------'  % (a * b / 1024 / 1024, c / 1024 / 1024, per)
	Printer(text)

def parseArgs():
	assert len(sys.argv) == 2, "Wrong arguments given."
	return True

def main(*args, **kwargs):
	"main function."
	if parseArgs():
		letv = Letv(sys.argv[1])
		letv.parse()

if __name__ == '__main__':
	main()