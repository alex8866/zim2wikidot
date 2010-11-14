#!/usr/bin/env python
# coding=utf-8
#
# Author: Chun-Yu Lee (Mat) <matlinuxer2@gmail.com>
#

import sys
import os
import zim.fs
import zim.notebook
import zim.templates
import subprocess
import tempfile
import shutil
import pdb
import xmlrpclib 
import conf

def upload( site, page, title, content_file ):
    # site: 指定該頁面要上傳的 site
    api_app_name, api_app_key = conf.get_api_name_and_key( site )
       
    if api_app_name == None or api_app_key == None:
        return False

    content = ""
    for line in file(content_file):
        content += line

    #print('https://%s:%s@www.wikidot.com/xml-rpc-api.php' % ( api_app_name, api_app_key ) )
    #print({'site' : site, 'page' : page, 'title' : title, 'source' : content})
    srvProxy = xmlrpclib.ServerProxy('https://%s:%s@www.wikidot.com/xml-rpc-api.php' % ( api_app_name, api_app_key ) )
    srvProxy.page.save({'site' : site, 'page' : page, 'title' : title, 'source' : content})

    return True

# notebook_path => NoteBook 的根目錄
# page_path     => 指定頁面的路徑,原始檔
# tmpfile_path  => 指定頁面的路徑,暫存檔
def main( notebook_path, page_path, tmpfile_path ):
    out_d = tempfile.mkdtemp()
    out_f = file( tempfile.mktemp(), 'a+' )

    tmpl_file = conf.get_template_file()

    # 設定轉出格式跟範本
    #tmpl = zim.templates.get_template('wiki', '_New')
    #tmpl = zim.templates.get_template('html', 'Default')
    tmpl = zim.templates.get_template('wiki', zim.fs.File(tmpl_file) )

    # 選定 Notebook
    ##nb = zim.notebook.get_default_notebook()
    nb = zim.notebook.get_notebook( zim.fs.Dir( notebook_path ) )

    # 取得當前的頁面項目
    nb_path = nb.resolve_file( notebook_path, notebook_path )
    pg_path = nb.resolve_file( page_path, notebook_path )

    path_array = [u'']
    path_array += pg_path.relpath( nb_path ).split('/')
    #path = zim.notebook.Path( path_array )
    path = ':'.join( path_array )
    if path[-4:] == u".txt":
        path = path[:-4]

    # 取得 ":xxx:yyy" zim 內用的頁面路徑
    page = nb.get_page( nb.resolve_path( path ) )
    #pdb.set_trace()

    lines = tmpl.process(nb, page )

    #sys.stdout.writelines( l.encode('utf-8') for l in lines )
    out_f.writelines( l.encode('utf-8') for l in lines  )
    out_f.close()

    # 用 zim 來顯示結果
    cmd = "zenity --text-info --filename=" + out_f.name
    subprocess.Popen([ cmd ], shell=True ).communicate()

    # TODO: 將 site, page, title 這三個參數用該頁的資料來取得 
    upload( "hackingthursday", "test2", "zim 2 wikidot 上傳測試...", out_f.name )
    
    # 執行完後，清掉暫存檔
    os.remove ( out_f.name )
    shutil.rmtree(out_d)


## 將下列這一行，安裝至 custom tools 的項目:
##   $( readlink -f zim2wikidot.py) %f %d %s %n %D %t
##
if __name__ == '__main__':
    if sys.argv.__len__() == 7:
        sys.argv[1]  # "%f: " => temperary
        sys.argv[2]  # "%d: " => file entry name
        sys.argv[3]  # "%s: " => real file path
        sys.argv[4]  # "%n: " => notebook
        sys.argv[5]  # "%D: " 
        sys.argv[6]  # "%t: " 
        
        print  sys.argv[4], sys.argv[3], sys.argv[1]
        main( sys.argv[4], sys.argv[3], sys.argv[1] )
