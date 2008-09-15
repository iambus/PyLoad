"""
A simple script to encode all the images the XRCed needs into a Python module
"""

import sys, os, glob
from wx.tools import img2py

def filelist(p):
    if type(p) == str:
        return glob.glob(p)
    elif type(p) == list or type(p) == tuple:
        return sum(map(glob.glob, p), [])
    else:
        raise TypeError('str, list, or tuple expected')

def main(filemask, output):
    # get the list of PNG files
    files = filelist(filemask)
    files.sort()

    # Truncate the inages module
    open(output, 'w')

    # call img2py on each file
    for file in files:

        # extract the basename to be used as the image name
        name = os.path.splitext(os.path.basename(file))[0]

        # encode it
        if file == files[0]:
            cmd = "-u -n %s %s %s" % (name, file, output)
        else:
            cmd = "-a -u -n %s %s %s" % (name, file, output)
        img2py.main(cmd.split())

    # Encode icons
    files = glob.glob('src-images/*.ico')
    files.sort()
    for file in files:
        # extract the basename to be used as the image name
        name = os.path.splitext(os.path.basename(file))[0]
        # encode it
        cmd = "-a -i -u -n %s %s %s" % (name, file, output)
        img2py.main(cmd.split())

if __name__ == "__main__":
    #main('src-images/*.png', 'images.py')
    #main('src-images/32x32/*.png', 'images_32x32.py')
    #main('src-images/*.gif', 'IconImages.py')
    main(['src-images/*.png', 'src-images/*.gif', 'src-images/*.ico'], 'IconImages.py')

