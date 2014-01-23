#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2014/01/21 lwldcr@gmail.com

# module for running tudou_digger.py,letv_digger.py, oc_digger.py

import sys,re,os

class ArgumentError(BaseException):
    pass

class MatchError(BaseException):
    pass

def parseArgs():
    """Parsing args,will return a tuple:
        (download_type, site)"""
    if not len(sys.argv) >= 2:
        raise ArgumentError , "Error: not enough arguments given!"
    if sys.argv[1] in [ '-f', '--file' ]:
         if len(sys.argv) != 3:
            raise ArgumentError, "Error: number of arguments should be 3!"
         assert os.path.isfile(sys.argv[2]), "Not a file: \"%s\"" % (sys.argv[2])
	 d_type = 2
	 kwd = sys.argv[2]     
    elif sys.argv[1] in [ '-l', '--list' ]:
        if len(sys.argv) != 3:
            raise ArgumentError, "Error: number of arguments should be 3!"
        d_type  = 1
        kwd = sys.argv[2]
    else:
        if len(sys.argv) != 2:
            raise ArgumentError, "Error: number of arguments should be 2!"
        d_type = 0
        kwd = sys.argv[1]
    return (d_type, kwd)

def import_digger(url):
    """Import suitable module as digger."""
    for k in [ 'tudou', 'youku', 'letv', '163', ]:
        if str(url).find(k) != -1:
            if k == '163':
                import opencourse_digger as digger
            else:
                if k == 'letv':
                    import letv_digger as digger
                else:
                    import tudou_digger as digger
            return digger
    raise MatchError, "Sorry, the given url \"%s\" is not currently supported!" % (url)

def parseFile(file):
    """Parsing input file when called."""
    try:
        f = open(file)
        fs = f.readlines()
        f.close()
    except:
        return []
    return fs

def main(*args, **kwargs):
    """Main function."""
    try:
        (d_type, kwd) = parseArgs()
    except ArgumentError, e:
        print e
        Usage()
	sys.exit(1)
    except MatchError, e:
        print e
        print """Currently supported sites are:
        opencourse.163.com
        tudou.com
        youku.com
        letv.com"""
        print "If you want any other sites supported, please contact me."
        sys.exit(1)
    
    if d_type == 2:
        urls = parseFile(kwd)
    else:
	urls = []
	urls.append(kwd)

    for url in urls:
	url = url.replace('\n','')
	if d_type == 1:
            args = ('-l', url)
    	else:
            args = (url)
	digger = import_digger(url)
    	function = getattr(digger, 'main')
    	function(args)

def Usage():
    """Usage info."""
    info = """Usage: 
    python main.py video_url
    python main.py [-l|--list] video_playlist
    python main.py [-f|--file] url_text"""
    print info

if __name__ == '__main__':
    main()
