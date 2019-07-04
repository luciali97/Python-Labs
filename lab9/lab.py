import sys
import doctest
from http009 import http_response

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!

CHUNK_SIZE = 8192
dash = '--'.encode('utf-8')
star = '(*)'.encode('utf-8')

def download_file(loc, cache = dict()):
    """
    Yield the raw data from the given URL, in segments of CHUNK_SIZE bytes.

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises a RuntimeError if the URL can't be reached, or in the case of a 500
    status code.  Raises a FileNotFoundError in the case of a 404 status code.
    """
    try:
        r = http_response(loc)
    except:
        raise RuntimeError

    while r.status in [301,302,307]:
        #  follow that redirect and try the location to which you are being redirected
        new_loc = r.getheader('location')
        r = http_response(new_loc)

    if r.status == 404:
        raise FileNotFoundError
    if r.status == 500:
        raise RuntimeError

    # handling manifests
    if loc[-6: ] == '.parts' or r.getheader('content-type') == 'text/parts-manifest':
        for x in file_manifests(r, cache):
            yield x
        return

    x = None
    while x is None or x != bytes():
        x = r.read(CHUNK_SIZE)
        if x != bytes():
            yield x
    return

def file_manifests(r, cache):

    def get_part(r):
        """ get a part of r
        Parameter:
            r (HTTPResponse object)
        Return:
            part (bytes): byte string of a part
            cacheable (bool): True iff (*) is in this part
        """
        x = None
        cacheable = False
        part = bytes()
        while x is None or (x[:-1] != dash and x[:-1] != bytes()):
            x = r.readline()
            if x[:-1] == star:
                cacheable = True
            if x[:-1] != star and x[:-1] != dash:
                part += x
        return part, cacheable

    # yield the bytes from each of the files specified in the manifest, 
    # in the order they are specified
    part = None
    while part is None or part != bytes():
        part, cacheable = get_part(r)
        in_cache = False
        found = False

        # If we reach a part that is marked as cacheable, we should first check to see if any of the URLs has been cached.
        # If so, we should simply use that result (without making any HTTP requests). 
        # If not, we should follow the normal procedure, but we should also store the result in the cache before continuing.
        if cacheable:
            for alt_url in part.decode().split('\n'):
                if alt_url in cache.keys():
                    in_cache = True
                    yield cache[alt_url]
                    found = True
                    break
        
        if not in_cache or not cacheable:            
            for alt_url in part.decode().split('\n'):
                if alt_url != '':
                    try:
                        for c in download_file(alt_url, cache):
                            yield c
                            if cacheable:
                                try:
                                    cache[alt_url] += c
                                except:
                                    cache[alt_url] = c 
                        found = True                         
                        break
                    except:
                        continue
                else:
                    found = True
        if not found:
            raise FileNotFoundError

def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.

    Note that each of the chunks yielded from download_file might contain multiple files, 
    or it might not contain an entire file. Your function will need to account for both of these cases.

    """
    file_length = bytes()
    file = bytes()

    for chuck in stream:
        i = 0
        while i < len(chuck):
            if len(file_length) < 4:
                k = 4 - len(file_length)
                file_length += chuck[i: i + (4 - len(file_length))]
                i += k
            else:
                j = int.from_bytes(file_length, byteorder = 'big') - len(file)
                # if this entire chuck is part of the current file 
                if len(chuck[i:]) < j:
                    file += chuck[i:]
                # otherwise, this chuck contains the tail of the current file
                else:
                    file += chuck[i: i+j]
                    yield file
                    file = bytes()
                    file_length = bytes()
                i = i+j

    if file != bytes():
        raise RuntimeError

    return

if __name__ == '__main__':

    url, filename = sys.argv[1], sys.argv[2]
    if (not isinstance(url, str) and not isinstance(url, bytes)) or not isinstance(filename, str):
        raise SyntaxError
    d = download_file(url)
    if '-seq' in url:
        d = files_from_sequence(d)
        for i, f in enumerate(d):
            file_i = open(filename+'-file%d'%i, 'wb')
            file_i.write(f)
            file_i.close()
    else:
        file = open(filename, 'wb')
        for f in d:
            file.write(f)
        file.close()


    ################### POSSIBLE ERRORS ###########################
    """
    1. If the link is invalid after redirects, then raise errors

    2. If all links in a part are invalid, then raise FileNotFoundError

    3. If the file sequence is not encoded correctly, i.e. not of the form 
        file1_length, file1, file2_length, file2,..., filek_length, filek,
        then raise RuntimeError

    4. If input url and filename are not str, raise SyntaxError 
    """

    pass
