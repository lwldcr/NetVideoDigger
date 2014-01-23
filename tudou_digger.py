#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2014/01/15 lwldcr@gmail.com

##########################
# Tudou video downloader #
##########################

import os,sys
import urllib,re
from time import time

outputDir = '/Volumes/HDD_OSX_Data/Video'

class videoHtml(object):
	def __init__(self,url='',vcode='',title=''):
		# setting initial variables
		self.rs = ''
		self.html = ''
		self.vhtml = ''
		self.qs = []
		self.vurl = ''
		self.title = title
		self.vcode = vcode
		self.q = ''
		self.k = ''
		self.parts = []
		self.ks = []
		self.vurls = []
		self.type = 0
		self.url = url

	def fetchHtml(self):
        	assert self.url
		if not self.url.startswith("http://"):
			self.url = 'http://' + self.url
		
		try:
			self.html = urllib.urlopen(self.url).read()
		except IOError as e:
			print "Html fetching failed: %s" % e
			return
        
		try:
			self.html = self.html.decode('gbk','ignore')
		except:
			self.html = self.html.decode('utf-8','ignore')

		if self.html:
			self.html = self.html
            # 首先尝试寻找segs字段，读取视频的k值
			self.rs = re.search(r'segs:\s*\'{(.*?)}]}\'', self.html)
			self.title = re.search(r',kw:\s*\"(.*?)\"', self.html)
		if not self.rs:
            # 如果未找到k，则尝试读取vcode
			self.vcode = re.search(r',vcode:\s*\'(.*?)\'', self.html)
			if not self.vcode:
				print "Cannot find proper video address!"
				return
			else:
				self.vcode = self.vcode.group(1)
        #正确分离到title后，提取出来
		if self.title:
			self.title = self.title.group(1)

	def parse(self):
		if self.rs:
			# 原创类视频
			self.parseKey()
			self.parseUrl()
			self.type = 0
		else:
			# 影视剧类视频，来源为优酷
			self.parseVcode()
			self.type = 1

	def parseKey(self):
		lines = self.rs.group(1).replace('"','').split('}],')
        	# 分离得到代表视频文件质量的代码
		self.q = int(lines[0].split(':')[0])
        
		i = 0
		flag = 0
        	# 遍历所有的信息，得到质量最高的self.q以及相应的序号flag
		for line in lines:
			if int(line.split(':')[0]) > self.q:
				self.q = int(line.split(':')[0])
				flag = i
			i = i + 1
		vString = lines[flag].split('[{')[1]
		vInfo = vString.split('},{')
        
        	# 得到视频文件的序号以及k值，存入self.parts，self.ks
		for info in vInfo:
			infoList = info.split(',')
			self.parts.append(infoList[1].split(':')[1])
			self.ks.append(infoList[3].split(':')[1])
		print self.parts,self.ks


	def parseUrl(self):
		"""parse video url"""
        	assert self.q
        	# 解析视频文件的真实地址，存入self.vurls
		baseUrl = 'http://v2.tudou.com/f?id='
		for k in self.ks:
			url = baseUrl + k
			try:
				self.vhtml = urllib.urlopen(url).read()
			except:
				pass

			if not self.vhtml:
				continue
			self.vurls.append(re.search(r'\<f.*?\>(http\:\/\/.*?)\</f', self.vhtml).group(1))
		print self.vurls

	def parseVcode(self):
		"""parse vcode"""
		#url = 'http://v.youku.com/player/getPlayList/VideoIDS/' + self.vcode
		url = 'http://v.youku.com/player/getPlayList/VideoIDS/' + self.vcode + '/timezone/+08/version/5/source/out/Sc/2?n=3&ran=9109&password='
		tempHtml = ''
		try:
			tempHtml = urllib.urlopen(url).read()
		except:
			pass

		try:
			tempHtml.decode('gbk','ignore')
		except:
			tempHtml.decode('utf-8','ignore')
        	
		# 获取解密的种子
		seed = int(re.search(r'\"seed\":(\d+)',tempHtml).group(1))
		# streamfileids,形如65*34*22*....的序列
		streamfs = re.search(r'\"streamfileids\":\{(.*?)\}', tempHtml).group(1)
		# 解析得到关键字的字典
        	d = {}
        	for stream in streamfs.replace('"','').split(','):
			(s,i) = stream.split(':')
			d[s] = i

        	ids = []
		# 依次尝试各种质量的视频，优先hd3，然后hd2，之后是mp4，最后flv
        	for stream in ['hd3','hd2','mp4','flv']:
            		try:
                		ids = d[stream].split('*')[:-1]
				break
            		except:
                		continue
		if stream == 'mp4':
			f_type = 'mp4'
		else:
			f_type = 'flv'

		# 解析具体地址
		s = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/\\:._-1234567890")
        	mixed = ''
        	while s:
			seed = (seed * 211 + 30031) & 0xFFFF
        		index = seed * len(s) >> 16
        		c = s.pop(index)
        		mixed += c
        	vid = ''.join(mixed[int(i)] for i in ids)

		pattern = r'\"%s\"\:\[\{(\"no\".*?)}]' % (stream)
		partinfos = re.search(pattern,tempHtml,re.S).group(1).split('},{')

		for partinfo in partinfos:
			info = partinfo.replace('"','').split(',')
			partno = info[0].split(':')[1]
			key = info[3].split(':')[1]
			no = '%02x' % int(partno)
			self.vurls.append('http://f.youku.com/player/getFlvPath/sid/00_00/st/%s/fileid/%s?K=%s' % (f_type, vid[:8]+no.upper()+vid[10:],key))
		return

def getFullname(partname):
	"""Get merged file name."""
	# 根据分段视频文件的名称得到合并后的文件名
	ns = re.search(r'(.*?)\-\d+\.([a-zA-Z0-9]+)', partname)
	try:
                (name, suffix) = ns.group(1), ns.group(2)
        except:
                print "Filename parsing error!"
                return
        fullname = name + '.' + suffix
	return (fullname, suffix)

class Printer():
	# 单行现实动态信息
	def __init__(self,data):
		sys.stdout.write("\r\x1b[K" + data.__str__())
		sys.stdout.flush()
	
def cbk(a, b, c): 
	"""Callback function for urllib.urlretrieve()"""
	# @a: 已经下载的数据块  @b: 数据块的大小  @c: 远程文件的大小
	per = 100.0 * a * b / c 
    	if per > 100: 
        	per = 100 
	text = '------Completed percentage: %.2f%%-------' % per
	Printer(text)

def judgeAvailable(filename, url):
	"""Judge if existing filename correctly downloaded from url."""
	# 判断已经下载的文件是否正确可用
	fLen = os.path.getsize(filename)
	p = urllib.urlopen(url)
	tLen = int(p.info().getrawheader('Content-Length').replace('\r\n',''))
	p.close()
	
	if fLen == tLen:
		return True
	else:
		return False
	
def download(url,title,type,i=0):
	"Download video from internet"
	url = url.replace('amp;','')
	if type == 0:
		suffix = re.search(r'http:\/\/.*?\/(.*?)\/',url).group(1)
	elif type == 1:
		suffix = re.search(r'http:\/\/.*?st\/(.*?)\/fileid', url).group(1)
	else:
		suffix = ''
	# 得到单个视频文件的名称
	filename = ''.join([title,'-','%02d' % i,'.',suffix])
	try:
		text_info = "Trying to download \"%s\"..." % (filename)
		print text_info
		fullname = getFullname(filename)[0]
		# 如果已经存在合适的文件，跳过此次下载
		if os.path.exists(fullname):
			print "File \"%s\" downloaded already, omitted." % (fullname)
			return
		elif os.path.exists(filename):
			if judgeAvailable(filename, url):
				print "File \"%s\" downloaded already, omitted." % (filename)
				return filename
			else:
				os.remove(filename)

		urllib.urlretrieve(url,filename, cbk)
		print "\nFile \"%s\" has been saved!" % (filename)
		return filename
	# 如果手动输入Ctrl-C中断程序，则删除未完成的下载
	except KeyboardInterrupt:
		print "\nManually interupted,cleaning..."
		if os.path.exists(filename):
			os.remove(filename)
		print "Done!"
		sys.exit(1)
	except:
		print "Downlaod failed!"
		return

def merge(files):
	"""Merge files into one."""
	(fullname, suffix) = getFullname(files[0])
	if suffix == 'flv':
		from flv_join import concat_flvs as concat
		
	elif suffix == 'mp4':
		from mp4_join import concat_mp4s as concat
	else:
		concat = ''
	
	if concat:
		concat(files, fullname)
		print "File:\"%s\" have been merged!" % (fullname)
        	print "Deleting temp files...",
        	for fp in files:
                	os.remove(fp)
        	print "Done"
       	else:
		print "File type not supported!"

def Usage():
	"Usage function."
	usageInfo = '''
Usage:
%s [v(ideo)|l(ist)] video_url
	''' % (sys.argv[0])
	print usageInfo
	sys.exit(0)

def judgeUrl(url):
	"Judge if given url suitable."
	if url.find('tudou') == -1:
		return 0
	return 1

def main(*args, **kwargs):
	"main function"
	assert len(sys.argv) == 3, Usage()
	if len(sys.argv) != 3:
		Usage()
	elif sys.argv[1] not in ['v','l']:
		Usage()
	if not judgeUrl(sys.argv[2]):
		print '***Illegal url given***'
		print 'Currently only \"tudou.com\" supported!'
		Usage()
	if not os.path.exists(outputDir):
		os.mkdir(outputDir)
	print '***Changing working directory to:\"%s\"' % (outputDir),
	try:
		os.chdir(outputDir)
		print "Done!"
	except:
		print "Failed! Will use \"%s\" as working directory." % (os.getcwd())
	print '--------Misson Launched---------'
	if sys.argv[1] == 'v':
		singleDownload(sys.argv[2])
	else:
		albumDownload(sys.argv[2])
	print '------Misson Accomplished-------'

def albumDownload(url):
	"""Album download function."""
	try:
		fs = urllib.urlopen(url).read().decode('utf-8')
	except:
		fs = urllib.urlopen(url).read().decode('gbk')
	
	if not fs:
		print "Cannot download given album!"
		return
	title = re.search(r'title:\s*\'(.*)\'\s*,',fs).group(1).encode('utf-8')
	try:
		print 'Entering list directory:\"%s\"' % (title),
		if not os.path.exists(title):
			os.mkdir(title)
		os.chdir(title)
		print 'Done!'
	except:
		print 'Failed!Use \"%s\" instead!"' % (os.getcwd())

	# 视频来源依然是youku，从soku链接解析视频地址
	soku_url = 'http://www.soku.com/v?keyword=' + repr(title).replace(r'\x','%')[1:-1]

	try:
		fs = urllib.urlopen(soku_url).read().decode('utf-8')
	except:
		fs = urllib.urlopen(soku_url).read().decode('gbk')
	if not fs:
		print "Cannot download given album!"
		return

	pattern = r'<a\s+href=\'(http\:\/\/.*?tudou.com/.*?.html)\'.*?\>(\d+)\<'
	# 得到所有的地址
	vs = re.findall(pattern, fs, re.S) 

	for (url,seq) in vs:
		singleDownload(url)

def singleDownload(url='',code='',title=''):
	"""Single download function."""
	# url 和 code必须有一个存在
	assert url or code, "Argument error!"
	if code:
		assert title
	if url:
		vHtml = videoHtml(url)	
		vHtml.fetchHtml()
	else:
		vHtml = videoHtml(vcode=code,title=title)
	vHtml.parse()
	files = []
	if vHtml.vurls:
		i = 0
		for url in vHtml.vurls:
			filename = download(url,vHtml.title, vHtml.type,i)
			if filename:
				files.append(filename)
			i += 1
	if files:
		merge(files)
		
if __name__ == '__main__':
	main()
