#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2014/1/20 lwldcr@gmail.com

########################################
# Netease opencourse video downloading #
########################################

import sys, os 
import re
import urllib

videoDir = 'D:\\Video\\'

class Course(object):
	def __init__(self,url=''):
		if self.testUrl(url):
			self.url = url
		self.vurls = []

	def parse(self):
		"Parse links."
		if self.fetchHtml():
			self.parseLinks()
		for link in self.ns:
			self.vurls.append(self.parseVlink(link[1]))

		if self.parseDir():
			# 推导得到将要下载的文件信息列表
			keylist = []
			i = 0
			#for (s,u,n) in self.ns:
			#	name = '-'.join([s,n])
			#	vurl = self.vurls[i]
			#	keylist.append((name,vurl))
			#	i = i + 1
			keylist = [ ('-'.join([s,n]), self.vurls[int(re.search(r'(\d+)',s).group(1)) - 1 ]) for (s,u,n) in self.ns ]
			for (name, vurl) in keylist:
				self.download(vurl,name)

	def parseDir(self):
		"Parse directory."
		try:
			vpath = os.path.join(videoDir, self.title)
			print "Changing directory to \"%s\"..." % vpath,
			if not os.path.exists(vpath):
				os.mkdir(vpath)
			os.chdir(vpath)
			print "done!"
		except:
			print "failed!\nUsing current directory \"%s\" instead!" % (os.path.join(os.getcwd(), self.title))
			if not os.path.exists(self.title):
				os.mkdir(self.title)
			os.chdir(self.title)
		return True

	def testUrl(self,url):
		"Test if given url available."
		assert url, "No url given!"
		assert str(url).find('163') != -1, "Not netease link given: \"%s\"" % (url)
		assert str(url).find('opencourse') != -1, "Not opencourse link given: \"%s\"" % (url)
		return True

	def fetchHtml(self):
		"Fetch html for parsing."
		hs = urllib.urlopen(self.url)
		self.html = hs.read()
		hs.close()

		try:
			self.html = self.html.decode('gbk','ignore')
		except:
			self.html = self.html.decode('utf-8', 'ignore')

		assert self.html, "Html fetching error: \"%s\"" % (self.url)
		return True

	def parseLinks(self):
		"Parse each class link from self.html."
		pattern = r'\<td class=\"u-ctitle\"\>\s*(\[.*?\])\s*\<a href=\"(http://.*?)\"\>(.*?)\<\/a\>'
		# 得到类似[(章节序号，链接，章节名),...]的数组
		ns = re.findall(pattern, self.html, re.S)
		# 去除重复元素
		self.ns = list(set(ns))

		try:
			self.title = re.search(r'\<h2\>(.*?)\<\/h2\>', self.html).group(1)
		except:
			self.title = "NoName"
		return self.ns

	def parseVlink(self, url):
		"Parse each video link."
		vs = urllib.urlopen(url)
		vc = vs.read()
		try:
			vc = vc.decode('utf-8')
		except:
			pass

		r = r'href=\"(http\:\/\/.*?.mp4)\"'
		try:
			vurl = re.search(r, vc).group(1)
		except:
			vurl = ''
		return vurl

	def download(self,vurl,name):
		"Download videos."
		urllib.socket.setdefaulttimeout(30)
		suffix = '.mp4'
		vname = (name + suffix).replace(':','-') # 不允许文件名包含':'
		if os.path.exists(vname):
			print '\"%s\" already exists!' % (vname)
			return True
		print 'start downloading \"%s\"...' % (vname)
		try:
			urllib.urlretrieve(vurl, vname, cbk)
			print '\n\"%s\" downloaded successfully!' % (vname)
		except IOError:
			print "\nNetwork error, deleting uncompleted files...",
			os.remove(vname)
			print "done!\nQuiting..."
			sys.exit(1)
		except KeyboardInterrupt:
			print "\nManually interrupted! Cleaning files...",
			os.remove(vname)
			print "done!\nQuiting..."
			sys.exit(1)
		return True

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
	text = '-------Completed percentage: %.2f%%------'  % per
	Printer(text)

def checkArgs():
	"""Check if arguments proper."""
	assert len(sys.argv) >= 2, "Argument not enough!"
	if sys.argv[1] in ['-l', '--list']:
		assert len(sys.argv) > 2, "Url list file not given!"
		return True
	return False

def Usage():
	"""Usage function."""
	info = """
Usage:
	python %s course_url
	python %s [-l | --list] url_file
	""" % (sys.argv[0], sys.argv[0])
	print info,
	sys.exit(1)

def main(*args, **kwargs):
	try:
		arg_type = checkArgs()
	except AssertionError, e:
		print e,
		Usage()
	if arg_type:
		try:
			f = open(sys.argv[2])
		except IOError, e:
			print e
			Usage()
		for url in f.readlines():
			download(url)
		f.close()
	else:
		download(sys.argv[1])

def download(url):
	"Download wrapper."
	course = Course(url)
	course.parse()

if __name__ == '__main__':
	main()
