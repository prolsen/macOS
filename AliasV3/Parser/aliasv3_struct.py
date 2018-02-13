```
The MIT License (MIT)

Copyright (c) 2016 Patrick Olsen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Patrick Olsen
```

import construct
from struct import unpack
from datetime import datetime, timedelta

class AliasV3Parser(object):
    def __init__(self, artifact_path):
        self.artifact_path = artifact_path

    def mactimeConvert(self, mactime):
        humantime = datetime(1904,1,1,0,0) + timedelta(0,int(float(mactime)))
        return(humantime)

    def absoluteConvert(self, absolute):
        try:
            return(datetime.datetime(2001,1,1,0,0,0) \
            + datetime.timedelta(0,absolute))
        except:
            return("Error on conversion")

    def ReturnAliasv3(self):
        cnidList = []
        results = []

        entryType = {
            1: 'Folder',
            0: 'File'
            }

        filesystemType = {
            '0000482b': 'H+'
            }

        ALIAS_STRUCT = construct.Struct(
            u'alias_header_struct',
            construct.Padding(4),
            construct.UBInt16(u'length'),
            construct.UBInt16(u'version'),
            construct.UBInt16(u'type'),
            construct.Padding(2),
            construct.UBInt32(u'cTime'),
            construct.Bytes(u'fileSystem', 4),
            construct.Padding(4),
            construct.UBInt32(u'parent_cnid'),
            construct.UBInt32(u'target_cnid'),
            construct.Padding(2),
            construct.UBInt32(u'vol_cTime'),
            #Unsure what this is, but it seems to be static among alias v3
            #Needs more research.
            construct.Padding(22),
            construct.UBInt32(u'num_of_cnids'),
            construct.Bytes("data", lambda ctx: (ctx.num_of_cnids / 65356)),
            construct.UBInt16('totalStringLen0'),
            construct.UBInt16('NameKeyLength'),
            construct.String('NameKey', lambda ctx: ctx.NameKeyLength*2),
            construct.UBInt16('unknownNum0'),
            construct.UBInt16('totalStringLen1'),
            construct.UBInt16('VolNameLength'),
            construct.String('VolName', lambda ctx: ctx.VolNameLength*2),
            construct.UBInt16('unknownNum1'),
            construct.UBInt16('PathLength'),
            construct.String('PathName', lambda ctx: ctx.PathLength)
        )

        #Return an object header of the parsed alias struct.
        header = ALIAS_STRUCT.parse(self.artifact_path)

        if header['version'] != 3:
            print 'Alias is not Version 3.  Check byte offset 7:8 for 0x0003.'

        num_of_cnids = len(header['data']) / 4

        for entry in unpack(">%dI" % num_of_cnids, header['data']):
            entry = entry / 65356
            #Convert to a string so we can join the output later.
            cnidList.append(str(entry))

        cTime = str(self.mactimeConvert(header['cTime']))
        vol_cTime = str(self.mactimeConvert(header['vol_cTime']))
        vol_fs_type = header['fileSystem'].replace('\000', '')
        target_type = entryType[header['type']]
        target_name = header['NameKey'].replace('\000', '')
        target_path = header['VolName'].replace('\000', '') + '/' \
            + header['PathName'].replace('\000', '')
        cnids = [x for x in cnidList]
        parent_cnid = str(header['parent_cnid'])
        target_cnid = str(header['target_cnid'])

        return(cTime, vol_cTime, vol_fs_type, target_type, target_name, \
               target_path, parent_cnid, target_cnid, ' '.join(cnids))
