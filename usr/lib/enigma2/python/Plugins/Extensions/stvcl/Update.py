import os, re, six
from twisted.web.client import downloadPage
print("stvcl.py")
def upd_done():        
    from twisted.web.client import downloadPage
    print( "In upd_done")
    xfile ='http://patbuweb.com/stvcl/stvcl.tar'
    print('xfile: ', xfile)
    if PY3:
        xfile = b"http://patbuweb.com/stvcl/stvcl.tar"
        print("Update.py in PY3")
    import requests
    response = requests.head(xfile)
    if response.status_code == 200:
        # print(response.headers['content-length'])
        fdest = "/tmp/stvcl.tar"
        print("Code 200 upd_done xfile =", xfile)
        downloadPage(xfile, fdest).addCallback(upd_last)
    elif response.status_code == 404:
        print("Error 404")
    else:
        return

def upd_last(fplug):
    import time
    time.sleep(5)        
    if os.path.isfile('/tmp/stvcl.tar') and os.stat('/tmp/stvcl.tar').st_size > 10000 : 
        import os
        cmd = "tar -xvf /tmp/stvcl.tar -C /"
        print( "cmd A =", cmd)
        os.system(cmd)
    return
    