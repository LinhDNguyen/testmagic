'''
Created on Mar 4, 2013

@author: mqx_test
'''
import datetime
from colorama import init, deinit, Fore, Style
import os
import re
import getopt
import shutil
import xml.dom.minidom


class Utility(object):
    '''
    classdocs
    '''

    @staticmethod
    def log(logstr):
        tmpstr = logstr
        #init for colorama
        init()
        #BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
        tmpstr = tmpstr.replace('<ck>', Fore.BLACK)
        tmpstr = tmpstr.replace('<cr>', Fore.RED)
        tmpstr = tmpstr.replace('<cg>', Fore.GREEN)
        tmpstr = tmpstr.replace('<cy>', Fore.YELLOW)
        tmpstr = tmpstr.replace('<cb>', Fore.BLUE)
        tmpstr = tmpstr.replace('<cm>', Fore.MAGENTA)
        tmpstr = tmpstr.replace('<ca>', Fore.CYAN)
        tmpstr = tmpstr.replace('<cw>', Fore.WHITE)
        tmpstr = tmpstr.replace('<cc>', Fore.RESET)
        tmpstr = tmpstr.replace('<sd>', Style.DIM)
        tmpstr = tmpstr.replace('<sb>', Style.BRIGHT)
        tmpstr = tmpstr.replace('<sn>', Style.NORMAL)
        tmpstr = tmpstr.replace('<sr>', Style.RESET_ALL)

        print(tmpstr)
        deinit()

    @staticmethod
    def clean_color(logstr):
        tmpstr = logstr
        #BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET
        tmpstr = re.sub(r'<c[krgybmawc]>', '', tmpstr)
        tmpstr = re.sub(r'<s[dbnr]>', '', tmpstr)
        return tmpstr

    @staticmethod
    def getDateOnly():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    @staticmethod
    def getDateStr():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def getDateTimeStr():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def getOsPath(orig_path):
        sep = os.sep
        return re.sub(r'[\\/]', sep, orig_path)

    @staticmethod
    def settings_to_hash(setting_str, assign_char='=', expr_char=';'):
        ret_map = {}

        expr_str = '\s*%s\s*' % expr_char
        assign_str = '\s*%s\s*' % assign_char
        srows = re.split(expr_str, setting_str)
        for srow in srows:
            sarr = re.split(assign_str, srow)
            if(len(sarr) != 2):
                print "ERR: size of assign exp is not 2.", sarr
            else:
                key = sarr[0]
                value = sarr[1]
                ret_map[key] = value
        return ret_map

    @staticmethod
    def args_to_hash(args, option_map):
        short_str = ''
        long_opts = []

        # Generate options list
        for key, val in option_map.items():
            if(key == 'NOT_OPT'):
                continue
            short_str += val['short']
            if(val['has_val']):
                short_str += ':'
                long_opts.append(val['long'] + "=")
            else:
                long_opts.append(val['long'])

        # get options and assign to map
        try:
            opts, args = getopt.getopt(args, short_str, long_opts)
            option_map['NOT_OPT'] = args

            for opt, val in opts:
                for key, opt_def in option_map.items():
                    if(key == 'NOT_OPT'):
                        continue
                    if(opt in ("-" + opt_def['short'],
                               "--" + opt_def['long'])):
                        if(opt_def['has_val']):
                            opt_def['value'] = val
                        else:
                            opt_def['value'] = True
                        break
        except Exception as ex:
            print "ERR:", ex

    @staticmethod
    def str_options(options_map):
        res_str = ''
        for key, val in options_map.items():
            if(key == 'NOT_OPT'):
                continue
            if(not val['value'] is None):
                res_str += "%20s" % key + ": {0}\n".format(val['value'])

        if(len(options_map['NOT_OPT']) > 0):
            res_str += "NOT options:\n"
            for nopt in options_map['NOT_OPT']:
                res_str += "\t{0}".format(nopt)
        return res_str

    @staticmethod
    def help_from_options(fname, options_map):
        res_str = fname + " "

        for key, val in options_map.items():
            if(key == 'NOT_OPT'):
                continue
            tmp_str = "["
            tmp_str += "-" + val['short']
            tmp_str += "|--" + val['long']
            if(val['has_val']):
                tmp_str += ' <value>'
            tmp_str += "]"

            res_str += tmp_str
        res_str += " [others]\n"

        # Detail options:
        res_str += "  Options:\n"

        for key, val in options_map.items():
            if(key == 'NOT_OPT'):
                continue
            tmp_str = '    -{0}|--{1} '.format(val['short'], val['long'])
            if(val['has_val']):
                tmp_str += '<value> '
            tmp_str += '\n'
            tmp_str += '      ' + val['desc'] + '\n'

            res_str += tmp_str

        return res_str

    @staticmethod
    def copy_tree(src_dir, dst_dir):
        """Copy tree from src to dst"""
        if(not os.path.exists(src_dir)):
            raise Exception("Source dir %s does not exists." % src_dir)
        if(not os.path.exists(dst_dir)):
            try:
                os.makedirs(dst_dir)
            except:
                pass
        for cur_src_dir, dirs, files in os.walk(src_dir):
            cur_dst_dir = cur_src_dir.replace(src_dir, dst_dir)
            if (not os.path.exists(cur_dst_dir)):
                os.makedirs(cur_dst_dir)
            for file in files:
                src_file = os.path.join(cur_src_dir, file)
                dst_file = os.path.join(cur_dst_dir, file)
                shutil.copy(src_file, dst_file)

    @staticmethod
    def parse_config(cfg_str):
        '''Parse specific config into hash.'''
        #specific config like this
        #block1:  {key1 = val1;key2=val2} \n block2:{key1=val1; key2=val2}
        # Blocks seperate by '}\n' ('}' folowed by '\n')
        # Each config seperated by ';'
        # key and value seperated by '='
        result_hash = {}
        if(cfg_str is None):
            return result_hash
        if(cfg_str.strip() == ''):
            return result_hash
        blocks = re.split(r'\s*\}\s*[\n\r]\s*', cfg_str)

        for block in blocks:
            block = block.strip()
            if(len(block) == 0):
                continue
            block = re.sub(r'\s*\}\s*$', '', block)
            operand_arr = re.split(r'\s*:\s*\{', block)
            block_name = operand_arr[0]
            block_val = operand_arr[1]

            result_hash[block_name] = {}

            # parse block value
            # 'key'='value';'key2' = 'value2';
            items_arr = re.split(r'\s*;\s*', block_val)
            for item in items_arr:
                item = item.strip()
                if(item == ''):
                    continue
                ipair = re.split(r'\s*=\s*', item)
                result_hash[block_name][ipair[0]] = ipair[1]

        return result_hash

    @staticmethod
    def add_to_zip(path, zipfile, rel_path=None):
        if(os.path.isdir(path)):
            # directory, add recusive
            for root, dirs, files in os.walk(path):
                for f in files:
                    abs_path = os.path.join(root, f)
                    rpath = abs_path
                    if(rel_path):
                        rpath = abs_path.replace(rel_path, '')
                        rpath = rpath[1:]

                    zipfile.write(rpath)
        elif(os.path.isfile(path)):
            # is file, add
            rpath = path
            if(rel_path):
                rpath = path.replace(rel_path, '')
                rpath = rpath[1:]
            zipfile.write(rpath)
        else:
            try:
                rpath = path
                if(rel_path):
                    rpath = path.replace(rel_path, '')
                    rpath = rpath[1:]
                zipfile.write(path)
            except:
                pass

    @staticmethod
    def parse_xml_config(fpath):
        result = {}
        xdoc = xml.dom.minidom.parse( fpath )

        # root document
        root = xdoc.childNodes[0]

        # browse each configuration
        for ele in root.childNodes:
            # Ignore text node
            if ele.nodeType == xdoc.TEXT_NODE:
                continue
            nname = ele.nodeName
            if nname != 'compilers':
                nvalue = ele.childNodes[0].nodeValue
                result[nname] = nvalue
            else:
                nvalue = {}
                for e in ele.childNodes:
                    # compilers
                    if e.nodeType == xdoc.TEXT_NODE:
                        continue
                    if e.nodeName != 'compiler':
                        continue
                    if not e.hasAttribute('name'):
                        continue
                    cname = e.getAttribute('name')
                    cpath = e.childNodes[0].nodeValue
                    nvalue[cname] = cpath
                result[nname] = nvalue

        return result
