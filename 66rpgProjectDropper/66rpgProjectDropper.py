import urllib3
import json
import base64
import re
import os
from pathlib import Path
import datetime
import hashlib
import hmac

OSS_ACCESS_KEY = ""
ACCESS_SECRET = ""

gameLink = input('请输入游戏链接、gindex 或 guid\n如 66rpg.com/game/17893、17893、或 5a9c559b69d8df96c2f7788ff6899133：\n')
print('正在获取版本信息...')


http = urllib3.PoolManager()
if len(gameLink) == 32:
    guid = gameLink
else:
    if '66rpg.com' in gameLink:
        gindex = gameLink[gameLink.rfind('/') + 1:len(gameLink)]
    elif str(int(gameLink)) == gameLink:
        gindex = gameLink

    # 通过gindex获取guid
    # 来自https://github.com/ssz66666/66rpg-spoofer
    gameLink = 'https://www.66rpg.com/f/' + gindex + '/ref/d3d3LjY2cnBnLmNvbQ=='
    body = str(http.request('GET', gameLink).geturl())
    guidIndex = body.find('guid=') + 5
    guid = body[guidIndex:guidIndex + 32]
    # 通过游戏链接获取guid，在网页中查找「"guid":"」即可
    # user_agent = {'user-agent': ''}
    # http = urllib3.PoolManager(10, headers=user_agent)
    # 不需要伪造UA
    # body = str(http.request('GET', gameLink).data)
    # guidIndex = body.find('"guid":"') + 8  # 「"guid":"」长8位
    # guid = body[guidIndex:guidIndex + 32]  # guid长32位

# 通过guid获取 gindex ver name uid create_time
# http://www.66rpg.com/api/common/versions?guid=$guid$
body = http.request('GET', 'http://www.66rpg.com/api/common/versions?guid=' + guid).data
jsonLoads = json.loads(body)
uid = str(jsonLoads['data'][-1]['uid'])
for n in range(len(jsonLoads['data'])):
    print('版本：' + str(jsonLoads['data'][n]['version']) + '  创建时间：' + str(jsonLoads['data'][n]['create_time']))
gameName = str(jsonLoads['data'][-1]['name'])
print(gameName + '  ' + guid)
latestVer = str(jsonLoads['data'][-1]['version'])
ver = input('请输入要下载的版本号，默认下载 ' + latestVer + '：\n')
if ver == '':
    ver = latestVer
print('正在获取文件列表...')
print('准备下载：' + gameName + '  版本' + ver)

# 通过guid+ver获取Map.bin
# http://wcdn1.cgyouxi.com/web/$guid$/$ver$/Map.bin
# 也可以使用网页客户端API下载压缩过后的游戏资源，格式json
# https://cgv2.66rpg.com/api/oapi_map.php?action=create_bin&guid=$guid$&version=$ver$&quality=32

# 解析map.bin中的文件名与MD5
lowercasefileName = []
MD5 = []
# Map.bin以「?? ?? 00 00 0D 00 00 00」开头，文件名与MD5以「?? ?? ?? 00 20 00 00 00」分隔，每行之间以「?? 00 00 00」分隔
# 文件大致为「?? ?? 00 00 0D 00 00 00 文件名_1 ?? ?? ?? 00 20 00 00 00 MD5_1 ?? 00 00 00 文件名_2.....」编码UTF-8
# 先分前者再分后者
mapBin = http.request('GET', 'http://wcdn1.cgyouxi.com/web/' + guid + '/' + ver + '/Map.bin').data
# print('http://wcdn1.cgyouxi.com/web/' + guid + '/' + ver + '/Map.bin')
mapbinHex = base64.b16encode(mapBin).decode()
mapbinHex = mapbinHex[16:]  # 切掉文件头
# 分割文件名和MD5，并保证后半部分剩余的hex不是奇数。否则 X[X XX XX X0 02 00 00 00 0]X 会匹配错误
mapbinHex = re.sub('......0020000000(?!.(..)*$)', '0D0A', mapbinHex)
mapbinHex = re.sub('..000000(?!.(..)*$)', '0D0A', mapbinHex)  # 分割行，并保证后半部分剩余的hex数据不是奇数。理由同上。
mapbinUTF8 = base64.b16decode(mapbinHex.encode()).decode('UTF-8')
mapbinUTF8 = str.split(mapbinUTF8, '\r\n')
lowercasefileName = mapbinUTF8[::2]  # 取偶数项
MD5 = mapbinUTF8[1::2]  # 取奇数项

# 更正fileName大小写
fileName = []
for name in lowercasefileName:
    name = name.replace('audio/bgm/', 'Audio/BGM/')
    name = name.replace('audio/se/', 'Audio/SE/')
    name = name.replace('audio/voice/', 'Audio/Voice/')
    name = name.replace('audio/bgs/', 'Audio/BGS/1')
    # name = name.replace('data/game.bin', 'Data/Game.bin')
    name = name.replace('data/game.bin', 'data/Game.bin')
    # name = name.replace('data/map.bin', 'Data/Map.bin')
    name = name.replace('data/map.bin', 'data/Map.bin')
    name = name.replace('font/', 'Font/')
    name = name.replace('graphics/background/', 'Graphics/Background/')
    name = name.replace('graphics/button/', 'Graphics/Button/')
    name = name.replace('graphics/face/', 'Graphics/Face/')
    name = name.replace('graphics/half/', 'Graphics/Half/')
    name = name.replace('graphics/mood/', 'Graphics/Mood/')
    name = name.replace('graphics/other/', 'Graphics/Other/')
    name = name.replace('graphics/system/', 'Graphics/System/')
    name = name.replace('graphics/transitions/', 'Graphics/Transitions/')
    name = name.replace('graphics/ui/', 'Graphics/UI/')
    name = name.replace('graphics/chat/', 'Graphics/Chat/')
    name = name.replace('graphics/oafs/', 'Graphics/Oafs/')
    fileName.append(name)

filePath = []  # 提出文件路径用于创建文件夹
for a in fileName:
    filepathIndex = a.rfind('/')
    filePath.append(a[:filepathIndex])

# 下载素材文件
# http://wcdn1.cgyouxi.com/shareres/$md5前两位$/$md5$
# 网页客户端的CDN为，似乎都可以使用
# https://dlcdn1.cgyouxi.com/shareres/$md5前两位$/$md5$
for i in range(len(fileName)):
    print(Path(gameName + '/' + fileName[i]), MD5[i])
    file = http.request('GET', 'http://wcdn1.cgyouxi.com/shareres/' + MD5[i][:2] + '/' + MD5[i]).data
    isExists = os.path.exists(Path(gameName + '/' + filePath[i]))
    if not isExists:  # 判断如果文件不存在,则创建
        os.makedirs(Path(gameName + '/' + filePath[i]))
    f = open(Path(gameName + '/' + fileName[i]), mode='wb')
    f.write(file)
    f.close()

print('素材文件下载完成')

if OSS_ACCESS_KEY == ACCESS_SECRET:
    os._exit(0)

print('准备下载工程文件')

# 工程文件储存在阿里云OSS中
# 隐藏在「other/StoryNew[0-9].data」、「other/Story[0-9].data」、「bin/Story.bin」这21个文件中
# 下载地址为
# http://ouser.oss.aliyuncs.com/$uid$/$guid$/$projectfilePath$
# 请求方式GET，请求头示例为
'''
GET /$uid$/$guid$/$projectfilePath$ HTTP/1.1
Host: ouser.oss.aliyuncs.com
Date: Mon, 27 Jul 2020 10:20:37 GMT
Authorization: OSS uEwcePgrON2VXsbv:$sign$
'''
HOST = "ouser.oss.aliyuncs.com"
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'

for i in range(11):
    for story in ['StoryNew', 'Story']:
        if i == 10:
            projectfilePath = 'bin/Story.bin'
        else:
            projectfilePath = 'other/' + story + str(i) + '.data'
        url = 'http://' + HOST + '/' + uid + '/' + guid + '/' + projectfilePath

        # 开始制作sign
        # sign为「GET\n\n\n$GMT$\n/ouser/$uid$/$guid$/$projectgamePath$」的HMAC-SHA1加密
        signInvalid = True
        while signInvalid:
            GMT = datetime.datetime.utcnow().strftime(GMT_FORMAT)  # 生成GMT时间
            signData = 'GET\n\n\n' + GMT + '\n/ouser/' + uid + '/' + guid + '/' + projectfilePath
            # 计算HMACsign
            key = bytes(ACCESS_SECRET, 'UTF-8')
            message = bytes(signData, 'UTF-8')
            digester = hmac.new(key, message, hashlib.sha1)
            signature1 = digester.digest()
            signature2 = base64.urlsafe_b64encode(signature1)
            sign = str(signature2, 'UTF-8')
            if '_' not in sign and '-' not in sign:  # 阿里云oss规定sign中不能含有-和_
                signInvalid = False

        headers = {
            'Host': HOST,
            'Date': GMT,
            'Authorization': 'OSS ' + OSS_ACCESS_KEY + ':' + sign
        }
        respone = http.request('GET', url, None, headers)
        if respone.status == 200:
            # isExists = os.path.exists(Path(gameName + '/Data'))
            # if not isExists:
            #    os.makedirs(Path(gameName + '/Data'))

            # f = open(Path(gameName + '/Data/Story.data'), mode='wb')
            # f.write(respone.data)
            f = open(Path(gameName + '/Data/StoryNew.data'), mode='wb')
            f.write(respone.data)
            # f = open(Path(gameName + '/avgEditor.avgmakerO'), mode='w')
            # f.write('')
            f = open(Path(gameName + '/avgEditor.avgmakerONew'), mode='w')
            f.write('')
            print(projectfilePath + ' ' + str(respone.status) + ' 工程文件下载成功！')
            os._exit(0)

        else:
            print(projectfilePath + ' ' + str(respone.status) + ' 文件获取失败')
            if i == 10:
                print('服务器中未找到工程文件，旧版工程可以尝试逆向Game.bin')
                os._exit(0)
