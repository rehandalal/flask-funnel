from __future__ import with_statement

import os
import re
import shutil
import subprocess
import urllib2

from flask import current_app
from flask.ext.script import Manager

from extends import preprocess

manager = Manager(usage="Asset bundling")


@manager.command
def bundle_assets():
    """Compress and minify assets"""
    YUI_COMPRESSOR_BIN = current_app.config.get('YUI_COMPRESSOR_BIN')

    path_to_jar = YUI_COMPRESSOR_BIN

    tmp_files = []

    def get_path(item):
        """Get the static path of an item"""
        return os.path.join(current_app.static_folder, item)

    def fix_urls(filename, compressed_file):
        """Fix relative paths in URLs for bundles"""
        print "Fixing URL's in %s" % filename

        def fix_urls_regex(url, relpath):
            """Callback to fix relative path"""
            url = url.group(1).strip('"\'')
            if url.startswith(('data:', 'http:', 'https:', 'attr(')):
                return url
            else:
                url = os.path.relpath(url, relpath)
                return 'url(%s)' % url

        css_content = ''
        with open(get_path(filename), 'r') as css_in:
            css_content = css_in.read()

        relpath = os.path.relpath(os.path.dirname(compressed_file),
                                  get_path(os.path.dirname(filename)))

        parse = lambda url: fix_urls_regex(url, relpath)

        css_parsed = re.sub('url\(([^)]*?)\)', parse, css_content)

        out_file = get_path(os.path.join(current_app.config.get('BUNDLES_DIR'),
                                         'tmp', '%s.tmp' % filename))

        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))

        with open(out_file, 'w') as css_out:
            css_out.write(css_parsed)

        return os.path.relpath(out_file, get_path('.'))

    def preprocess_file(filename, compressed_file):
        """Preprocess the file"""
        if filename.startswith('//'):
            url = 'http:%s' % filename
        elif filename.startswith(('http:', 'https:')):
            url = filename
        else:
            url = None

        if url:
            ext_media_path = get_path('external')

            if not os.path.exists(ext_media_path):
                os.makedirs(ext_media_path)

            filename = os.path.basename(url)
            if filename.endswith(('.js', '.css', '.less')):
                fp = get_path(filename.lstrip('/'))
                file_path = os.path.join(ext_media_path, fp)

                try:
                    req = urllib2.urlopen(url)
                    print ' - Fetching %s ...' % url
                except urllib2.HTTPError, e:
                    print ' - HTTP Error %s for %s, %s' % (url, filename,
                                                           str(e.code))
                    return None
                except urllib2.URLError, e:
                    print ' - Invalid URL %s for %s, %s' % (url, filename,
                                                            str(e.reason))
                    return None

                with open(file_path, 'w+') as fp:
                    try:
                        shutil.copyfileobj(req, fp)
                    except shutil.Error:
                        print ' - Could not copy file %s' % filename
                filename = os.path.join('external', filename)
            else:
                print ' - Not a valid remote file %s' % filename
                return None

        filename = preprocess(filename.lstrip('/'))

        if url is None and filename.endswith('.css'):
            filename = fix_urls(filename, compressed_file)
            tmp_files.append(filename)

        return get_path(filename.lstrip('/'))

    def minify(ftype, file_in, file_out):
        """Minify the file"""
        if ftype == 'js' and 'UGLIFY_BIN' in current_app.config:
            o = {'method': 'UglifyJS',
                 'bin': current_app.config.get('UGLIFY_BIN')}
            subprocess.call("%s -o %s %s" % (o['bin'], file_out, file_in),
                            shell=True, stdout=subprocess.PIPE)
        elif ftype == 'css' and 'CLEANCSS_BIN' in current_app.config:
            o = {'method': 'clean-css',
                 'bin': current_app.config.get('CLEANCSS_BIN')}
            subprocess.call("%s -o %s %s" % (o['bin'], file_out, file_in),
                            shell=True, stdout=subprocess.PIPE)
        else:
            o = {'method': 'YUI Compressor',
                 'bin': current_app.config.get('JAVA_BIN')}
            variables = (o['bin'], path_to_jar, file_in, file_out)
            subprocess.call("%s -jar %s %s -o %s" % variables,
                            shell=True, stdout=subprocess.PIPE)

        print "Minifying %s (using %s)" % (file_in, o['method'])

    # Assemble bundles and process
    bundles = {
        'css': current_app.config.get('CSS_BUNDLES'),
        'js': current_app.config.get('JS_BUNDLES'),
    }

    for ftype, bundle in bundles.iteritems():
        for name, files in bundle.iteritems():
            concatenated_file = get_path(os.path.join(
                current_app.config.get('BUNDLES_DIR'), ftype,
                '%s-all.%s' % (name, ftype,)))
            compressed_file = get_path(os.path.join(
                current_app.config.get('BUNDLES_DIR'), ftype,
                '%s-min.%s' % (name, ftype,)))

            if not os.path.exists(os.path.dirname(concatenated_file)):
                os.makedirs(os.path.dirname(concatenated_file))

            all_files = []
            for fn in files:
                processed = preprocess_file(fn, compressed_file)
                print 'Processed: %s' % processed
                if processed is not None:
                    all_files.append(processed)

            # Concatenate
            if len(all_files) == 0:
                print "Warning: '%s' is an empty bundle." % bundle

            all_files = ' '.join(all_files)

            subprocess.call("cat %s > %s" % (all_files, concatenated_file),
                            shell=True)

            # Minify
            minify(ftype, concatenated_file, compressed_file)

            # Remove concatenated file
            print 'Remove concatenated file'
            os.remove(concatenated_file)

    # Cleanup
    print 'Clean up temporary files'
    for file in tmp_files:
        try:
            os.remove(get_path(file))
            os.rmdir(os.path.dirname(get_path(file)))
        except OSError:
            pass

    try:
        os.rmdir(get_path(os.path.join(current_app.config.get('BUNDLES_DIR'),
                                       'tmp')))
    except OSError:
        pass
