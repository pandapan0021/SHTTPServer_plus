# -*-coding: utf-8 -*-
#!/usr/bin/python

'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
             SHTTPServer_plus.py
------------------------------------------------
  enhance the standard library http/server.py to
support upload file

test in python3.5
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

import os, sys, urllib, urllib.parse, http, html, io
import argparse

try:
    from http.server import SimpleHTTPRequestHandler, test
except ImportError:
    from SimpleHTTPServer import SimpleHTTPRequestHandler, test


class SRequestHandler(SimpleHTTPRequestHandler):
    """Add :meth:`do_POST` handle the post request


    """
    def do_POST(self):
        f = self.send_head()
        self.copyfile(f, self.wfile)
        
        # read from the socket accepted.
        lines = self.rfile.read().split(b'\r\n')

        # http request when upload:
        #;;;;
        # Method url Version
        # 
        # headers
        # 
        # BOUNDARY
        # Content-Disposition: form-data; name=...; filename=...
        # Content-Type:...
        # 
        # (file data)
        # BOUNDARY
        #;;;;
        file_info = lines[1]
        filename = file_info.split(b";")[2].split(b"=")[1][1:-1]
        data = lines[4: -2]
        data = b'\r\n'.join(data)

        try:
            f = open(filename, "wb")
        except:
            raise Exception("Can't open s%" % filename)
        else:
            f.write(data)
        finally:
            f.close()

        # redirect to index
        # Not implement

        f.close()

    def list_directory(self, path):
        """ generator page
        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(404, "NO permission to list ddireectory")
            return None
        list.sort(key=lambda a: a.lower())
        r=[]
        try:
            displaypath = urllib.parse.unquote(self.path, errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append('<li><a href="%s">%s</a></li>'
                    % (urllib.parse.quote(linkname,
                                          errors='surrogatepass'),
                       html.escape(displayname)))
        r.append('</ul>\n<hr>\n')
        #;;;
        # append for upload file
        r.append('<form enctype="multipart/form-data" method="POST">\n')
        r.append('<input name="tt" type="file"/>\n')
        r.append('<input type="submit"/>\n')
        r.append('</form>\n')
        #;;;
        r.append('</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', 'b', default='', metavar='ADDRESS',
                        help='Specify alternte bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store', 
                        default=8000, type=int,
                        nargs='?',
                        help='Specify altername port [default: 8000]')
    args = parser.parse_args()
    test(HandlerClass=SRequestHandler, port=args.port, bind=args.bind)
