#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import os
import json
import shutil
import rarfile
from py7zr import pack_7zarchive, unpack_7zarchive
from docx import Document
import pandas as pd
from id_validator import validator
from urllib.parse import urlparse
from utils import tree, tree2list
from utils import reader, traverse
from modules.btbu.util import find_idcard
from paths import DOWNLOADS, DUMP_HOME
from libs.logger import logger

# https://bbs.huaweicloud.com/blogs/180864
# register file format at first.
shutil.register_archive_format('7zip',
                               pack_7zarchive,
                               description='7zip archive')
shutil.register_unpack_format('7zip',
                              ['.7z'],
                              unpack_7zarchive,
                              description='7zip archive')


def load2find(path):
    files = traverse(path)
    results = dict()
    for filepath in files:
        filename = os.path.basename(filepath)
        candidates = list()
        try:
            if re.match(r'.*\.(txt|csv|xml|json)$', filepath, re.I):
                for line in reader(filepath):
                    candidates.extend(find_idcard(line))
            elif re.match(r'.*\.doc[x]?$', filepath, re.I):
                logger.info("Load: '%s'" % filepath)
                # docx.opc.exceptions.PackageNotFoundError: Package not found at ''
                doc = Document(filepath)
                for p in doc.paragraphs:
                    candidates.extend(find_idcard(p.text))
            elif re.match(r'.*\.xls[x]?$', filepath, re.I):
                logger.info("Load: '%s'" % filepath)
                # ValueError: Excel file format cannot be determined, you must specify an engine manually.
                xls = pd.read_excel(filepath, sheet_name=None)
                for name, sheet in xls.items():
                    for index, row in sheet.iterrows():
                        for value in row:
                            candidates.extend(find_idcard(str(value)))
        except Exception as e:
            logger.error(e)
        if len(candidates) > 0:
            results[filename] = list(set(candidates))
    return results


def unarchive(path):
    files = traverse(path)
    results = tree()
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            dest_dir = ''
            if re.match(r'.*\.(zip|7z|tar|tar\.bz2|tar\.gz|tar\.xz|tbz2|tgz|txz)$', filepath, re.I):
                dest_dir = filepath + '.unpack'
                # shutil.ReadError: xxx.zip is not a zip file
                shutil.unpack_archive(filepath, dest_dir)
            elif filename.endswith('.rar'):
                rarfile.UNRAR_TOOL = r"C:\OptSoft\unrar\UnRAR.exe"
                rar = rarfile.RarFile(filepath)
                dest_dir = filepath + '.unpack'
                with rar as rf:
                    rf.extractall(dest_dir)
            #
            if dest_dir:
                ret = load2find(dest_dir)
                pkg_name = filename
                if len(ret) > 0:
                    results[pkg_name] = ret
            else:
                ret = load2find(filepath)
                pkg_name = ''
                if len(ret) > 0:
                    results[pkg_name][filename] = ret[filename]
        except Exception as e:
            logger.error(e)
    return results


def dump2csv(infos):
    df = pd.DataFrame(tree2list(infos), columns=['archive', 'filename', 'idcard'])
    df = df.assign(idcard=df["idcard"]).explode("idcard").reset_index(drop=True)
    df['is_valid'] = df['idcard'].map(lambda x: 1 if validator.is_valid(x) else 0)
    with open(os.path.join(DUMP_HOME, 'file_urls.json')) as fopen:
        file_urls = json.load(fopen)
    fname2url = dict()
    for file_url in file_urls:
        filename = os.path.basename(urlparse(file_url).path)
        fname2url[filename] = (file_urls[file_url], file_url)
    csv = list()
    for index, row in df.iterrows():
        filename = row['archive'] if row['archive'] else row['filename']
        url, file_url = '', ''
        if filename in fname2url:
            url, file_url = fname2url[filename]
        csv.append(dict(zip(['url', 'file_url', 'archive', 'filename', 'idcard', 'is_valid'],
                            [url, file_url, row['archive'], row['filename'], row['idcard'], row['is_valid']])))
    pd.DataFrame(csv).to_csv(os.path.join(DUMP_HOME, 'file_results.csv'))


if __name__ == '__main__':
    # print(json.dumps(unarchive(os.path.join(os.path.dirname(__file__), 'test')), indent=4))
    # print(json.dumps(unarchive(DOWNLOADS)))
    infos = unarchive(DOWNLOADS)
    print(json.dumps(infos))
    # infos = {"20090708104206.xls":["510102192201118444","142701196410161283","220104196401151547","142224197310280025","110107196202241121","130102196706071586","11010219510516114x","372501197409081178","150430197209111620","140103196406205720","150102197410094541","360102197401176341","210211197310140043","140102197101205189","220203197303200329","370602197210143415","11010219571025239x","230107196812180423","110107197401150032","110224197406083811","110108197212213715","220104196909090925","62010219760502532x","370823196807041129","610403197302250053","110103196608130944","433024197008130084","220202196305222440","14260219750408152x","130603196809230977","110108196712091430","510126197102160357","612101197409090830","342324196511057215","372801197702077481","372927197105270522","37010419731012302x","11011119680202001x","132427197602291824","650103197211270025","210103197201241827","140103195911086318","110108196505315465","610103196806112497","110107196212050687","110225196809136510","142701197110042420","420111196502287313","140121197507303511","622301196202201722","350102196811180486","110108197612075411","230602197103135726","430407197206042758","410105197602131020","130705196608280626","130104196304171384","130102196702090667","320211196909233431","342425197207305516","410928197506029614","370102196612243337","320106195604070853","310104197210045617","610113197504021626","150102197305231516","42010719721207001x","610113197608201613","230103197008025114","140402197302143240","110108197412175418","620102196504235411","510721197201029429","433102196304010020","220103197012072923","110223197408311068","110111196211153638","432503197708298026","610104197507106127","432501197404220024","11010819701013543x","110108195911235711","420111197010044088","41302119741112006x","622801197402240023","410305197402214017","230602196306105741","110108197407065417","142431197510170044","230103196502125159","370121196510296824","510102197001128410","140103196105026323","142322197210192514","410105197209122742","220104197407052616","110104197611160467","420106197008154092","110102197502030820","36010419741127102x","432623197105128520"],"20100824023927.xls":["220112197001011210"],"20160316194608888452.xlsx":["038900000000000004","051399999999999994"],"20160318075357976152.xlsx":["051399999999999994","054400000000000004","044500000000000005"],"20160318075446188226.xlsx":["051635443828956795","016652417706353617","041088660932977916","021735531616116077","021135450630346497","036161443368222024","025046364889682593","036070759951435605","037239457587382674","041044250522354275","061685571017008556","028596160327531095","024410481621167435","031538707298622626","021673298579258926","033818976988627014","032154517712562836","056903922722256084","060274592229255575","029521397773102365","031250073760283215","041934267652806057","036389899128934644","046150971102463245","022252392648127284","055233244494644396","055473439489546195","044377681022382376","036587097189048734","023217987287324604","027302762064735475","032885760515867446","032540116083126236","008974958041143566","038098722168207644","030371389245217983","026920625760560313","026297669756331743","024683962645475788","059063782455361036","031032142282306552","028728863706191987","048294022322295405","009209155527130974","031996455478214614","007817303586918456","012315610779538133","015279598342843315","019089137236562692","060625683444300194","047994021444225154","055319728534136914","024474114480852904","003860188790163477","028213078565663352","033533924074703236","053625381763254154","036080857726680904","047826534312875424","049278865995304955","054287874698871974","028706179367947726","001025965707476928","043158578860492014","001612219447821417","048437406169220765","061156331013087595","055277657638690414","059944567003569205","051114356533446426","031372125919489235","020651501694551655","009162006469736639","021889885527293984","043464025765665326","034857445136530885","034544277365789355","016443026120576576","034615449476980586","049644192878155025","047795746490983504","038954086971493496","020707398393952303","027292125647974785","030483786565461912","050894581253835725","059631123073614845","049153236595294914","052004359404776324","057947139126028446","051349007701517735","042750441457265254","034639308340764785","003434809118608939","031196352597198995"],"20181022165851873835.xlsx":["052405999999999994","043826000000000004","041513999999999995"],"20191028190157920643.xlsx":["047599999999999996","058499999999999996"],"20210311160228771454.xlsx":["060599999999999994","047599999999999996","058499999999999996"],"4ab8b55b8a0d4bd492d6141cabf3111e.docx":["121100004006906889"],"77e58406d3f64ce89e839faab70ddade.xls":["027777777777777776"],"88e3c9a5f04041d581cfbb8e0befd16b.docx":["121100004006906889"],"a88d0dcffca047728d45053027f8d43f.xlsx":["43010219750520101X"],"cba523e1b44347428fa7b7c0a15485c9.docx":["121100004006906889"]}
    dump2csv(infos)




