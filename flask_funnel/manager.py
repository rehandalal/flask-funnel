import os
import re
import shutil
import subprocess
import urllib2

from flask import current_app
from flask.ext.script import Manager

manager = Manager(usage="Asset bundling")

@manager.command
def bundle_assets():
    """Compress and minify assets"""

    LESS_BIN = current_app.config.get('LESS_BIN', 'lessc')

    path_to_jar = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                'bin',
                                                'yuicompressor-2.4.7.jar'))

    def get_path(item):
        return os.path.join(current_app.static_folder, item)

    def fix_urls(filename, ftype):
        print "Fixing URL's in %s" % filename

        def fix_urls_regex(url, relpath):
            url = url.group(1).strip('"\'')
            if url.startswith(('data:', 'http:', 'https:')):
                return url
            else:
                url = os.path.relpath(url, relpath)
                return 'url(%s)' % url

        css_content = ''
        with open(get_path(filename), 'r') as css_in:
            css_content = css_in.read()

        bundle_path = get_path(os.path.join('bundle', ftype))

        relpath = os.path.relpath(bundle_path,
                                  get_path(os.path.dirname(filename)))
        parse = lambda url: fix_urls_regex(url, relpath)
        css_parsed = re.sub('url\(([^)]*?)\)', parse, css_content)

        out_file = get_path(os.path.join('bundle', 'tmp', '%s.tmp' % filename))

        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))

        with open(out_file, 'w') as css_out:
            css_out.write(css_parsed)

        return os.path.relpath(out_file, get_path('.'))

    def process_file(filename, ftype):
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
        else:
            filename = fix_urls(filename, ftype)

        if filename.endswith('.less'):
            fp = get_path(filename.lstrip('/'))
            subprocess.call('%s %s %s.css' % (LESS_BIN, fp, fp),
                            shell=True, stdout=subprocess.PIPE)
            filename = '%s.css' % filename
        return get_path(filename.lstrip('/'))

    def minify(ftype, file_in, file_out):
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
            variables = (o['bin'], path_to_jar, file_in, file_out)
            subprocess.call("%s -jar %s %s -o %s" % variables,
                       shell=True, stdout=subprocess.PIPE)

        print "Minifying %s (using %s)" % (file_in, o['method'])

    bundles = {'css': current_app.config.get('CSS_BUNDLES'),
               'js': current_app.config.get('JS_BUNDLES'),}

    for ftype, bundle in bundles.iteritems():
        for name, files in bundle.iteritems():
            concatted_file = get_path('bundle/%s/%s-all.%s'
                                      % (ftype, name, ftype,))
            compressed_file = get_path('bundle/%s/%s-min.%s'
                                       % (ftype, name, ftype,))

            if not os.path.exists(os.path.dirname(concatted_file)):
                os.makedirs(os.path.dirname(concatted_file))

            all_files = []
            for fn in files:
                processed = process_file(fn, ftype)
                if processed is not None:
                    all_files.append(processed)

            # Concatenate
            if len(all_files) == 0:
                print "Warning: '%s' is an empty bundle." % bundle
            subprocess.call("cat %s > %s" %
                            (' '.join(all_files), concatted_file), shell=True)

            # Minify
            minify(ftype, concatted_file, compressed_file)

    # Cleanup
    print 'Clean up temporary files'
    shutil.rmtree(get_path(os.path.join('bundle', 'tmp')))
