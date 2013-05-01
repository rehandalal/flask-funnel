from __future__ import with_statement

import os
import re
import shutil
import subprocess
import urllib2

from flask import current_app
from flask.ext.script import Manager

from extends import produce, mapping as extend_mapping

manager = Manager(usage="Asset bundling")
validate_postfix = [postfix for postfix, _, _ in extend_mapping]

@manager.command
def bundle_assets():
    """Compress and minify assets"""

    YUI_COMPRESSOR_BIN = current_app.config.get('YUI_COMPRESSOR_BIN')

    tmp_files = []

    def get_path(item):
        """Get the static path of an item"""
        return os.path.join(current_app.static_folder, item)

    def fix_urls(filename, compressed_file):
        # TODO : different type to encoding
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
            if not any(filename.endswith(i) for i in validate_postfix):
                print ' - Not a valid remote file %s' % filename
                return None

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

        if url is None and filename.endswith('.css'):
            # hack to css
            filename = fix_urls(filename, compressed_file)
            tmp_files.append(filename)

        return get_path(filename.lstrip('/'))

    def minify(ftype, file_in, file_out):
        """Minify the file"""
        if ftype == 'js' and current_app.config.has_key('UGLIFY_BIN'):
            o = {'method': 'UglifyJS',
                 'bin': current_app.config.get('UGLIFY_BIN')}
            subprocess.call("%s -o %s %s" % (o['bin'], file_out, file_in),
                            shell=True, stdout=subprocess.PIPE)
        elif ftype == 'css' and current_app.config.has_key('CLEANCSS_BIN'):
            o = {'method': 'clean-css',
                 'bin': current_app.config.get('CLEANCSS_BIN')}
            subprocess.call("%s -o %s %s" % (o['bin'], file_out, file_in),
                       shell=True, stdout=subprocess.PIPE)
        else:
            o = {'method': 'YUI Compressor',
                 'bin': current_app.config.get('JAVA_BIN')}
            variables = (o['bin'], YUI_COMPRESSOR_BIN, file_in, file_out)
            subprocess.call("%s -jar %s %s -o %s" % variables,
                       shell=True, stdout=subprocess.PIPE)

        print "Minifying %s (using %s)" % (file_in, o['method'])

    # Assemble bundles and process
    bundles = {'css': current_app.config.get('CSS_BUNDLES'),
               'js': current_app.config.get('JS_BUNDLES'),}

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
                processed = produce(fn, compressed_file)
                if processed is not None:
                    all_files.append(processed)

            # Concatenate
            if len(all_files) == 0:
                print "Warning: '%s' is an empty bundle." % bundle

            subprocess.call("cat %s > %s" %
                (' '.join(all_files), concatenated_file), shell=True)

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
            shutil.rmtree(os.path.dirname(get_path(file)))
        except OSError:
            pass

    try:
        shutil.rmtree(
            get_path(os.path.join(current_app.config.get('BUNDLES_DIR'),
                                  'tmp')))
    except OSError:
        pass
