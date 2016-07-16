#!/usr/bin/env python3
#
# Licensed to you under the MIT license.  See the LICENSE file in the
# project root for more information.

import miktex.packaging.info.inifile
import miktex.packaging.info.md5
import miktex.packaging.info.texcatalogue
import miktex.packaging.settings.paths
import miktex.packaging.util.filesystem
import os
import subprocess
import sys

def unpack_tds_zip_file(tds_zip_file, dest_dir):
  os.mkdir(dest_dir)
  subprocess.call([miktex.packaging.settings.paths.UNZIP_EXECUTABLE, "-qq", tds_zip_file, "-d", dest_dir])
    
def run_tdsutil(package, source_dir, dest_dir):
    tdsutil = [miktex.packaging.settings.paths.TDSUTIL_EXECUTABLE]
    tdsutil.append("--verbose")
    tdsutil.append("--source-dir=" + source_dir)
    tdsutil.append("--dest-dir=" + dest_dir)
    tdsutil.append("--recipe=" + os.path.normpath(miktex.packaging.settings.paths.TDSUTIL_DEFAULT_RECIPE))
    package_recipe_file = os.path.normpath(os.path.join(miktex.packaging.settings.paths.TDSUTIL_RECIPE_DIR,
                                                        package + ".ini"))
    if os.path.isfile(package_recipe_file):
        tdsutil.append("--recipe=" + package_recipe_file)
    tdsutil.append("install")
    tdsutil.append(package)
    subprocess.call(tdsutil)

def archive_source_files(package, dest_dir):
    source_file_dir = os.path.normpath(os.path.join(dest_dir, "source"))
    if not os.path.isdir(source_file_dir):
        return
    for suffix in [".cab", ".tar.bz2", ".tar.xz"]:
        to_be_removed = os.path.join(source_file_dir, package + "-src" + suffix)
        if os.path.isfile(to_be_removed):
            os.remove(to_be_removed)
    archife_file = os.path.join(source_file_dir, )
    subprocess.call(miktex.packaging.settings.paths.TAR_EXECUTABLE + " -cJf " + package + "-src.tar.xz *",
                    cwd=source_file_dir,
                    shell=True)
    subdirs = []
    for entry in os.scandir(source_file_dir):
        if entry.is_dir():
            subdirs.append(entry.path)
    for subdir in subdirs:
        miktex.packaging.util.filesystem.remove_directory(subdir)
    
if len(sys.argv) != 2:
    sys.exit("Usage: " + sys.argv[0] + " <package-name>")

package = sys.argv[1]
entry = miktex.packaging.info.texcatalogue.Entry(package)
if not entry.is_free():
    sys.exit("package '" + package + "' has a license issue")
if entry.ctan_path == None:
    sys.exit("package '" + package + "' has no ctan_path")
source_dir = os.path.normpath(miktex.packaging.settings.paths.MIKTEX_CTAN + entry.ctan_path)
if not os.path.isdir(source_dir):
    sys.exit("'" + source_dir + "' is not a directory")
dest_dir = os.path.normpath(miktex.packaging.settings.paths.get_texmf_dir(package))
if os.path.isdir(dest_dir):
    miktex.packaging.util.filesystem.remove_directory(dest_dir)
tds_zip_file = os.path.normpath(miktex.packaging.settings.paths.MIKTEX_CTAN + "/install" + entry.ctan_path + ".tds.zip")
if os.path.isfile(tds_zip_file):
    unpack_tds_zip_file(tds_zip_file, dest_dir)
else:
    run_tdsutil(package, source_dir, dest_dir)
miktex.packaging.util.filesystem.remove_empty_directories(dest_dir)
archive_source_files(package, dest_dir)
miktex.packaging.info.inifile.write_ini_file(package, entry, miktex.packaging.info.md5.try_get_md5(package))
