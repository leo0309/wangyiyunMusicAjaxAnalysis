from netEaseMusicEncrypt import rand_a, netEase_AES_encrypt,  \
                                netEase_RSA_encrypt_NoPadding,dictSerialize,aes_encrypt

query ={"s":"张惠妹","limit":"8", "csrf_token":""}
key1 = "0CoJUm6Qyw8W8jud"
iv = "0102030405060708"

#公钥对，hex16进制编码
module="00e0b509f6259df8642dbc35662901477df22677ec152b5ff68a\
ce615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
publickey = "010001" 
#序列化查询dict
queryStr = dictSerialize(query)
print('queryStr:',queryStr)

aaa = aes_encrypt(queryStr,key1,iv)
print(aaa)
#AES加密随机量
key2 = rand_a()
print('key2:',key2)
secretStr = netEase_AES_encrypt(queryStr,key1,key2,iv)
print('加密后params：',secretStr)

rsaSec = netEase_RSA_encrypt_NoPadding(key2,publickey,module)
print('加密后encSecKey',rsaSec)
import requests 

headers = {
    'Cookie': 'appver=1.5.0.75771;',
    'Accept-Encoding':'gzip, deflate',
    'Content-Type':'application/x-www-form-urlencoded',
    'Host':'music.163.com',
    'Origin':'http://music.163.com',
    'Proxy-Connection':'keep-alive',
    'Pragma':'no-cache',
    'Referer':'http://music.163.com/',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
}

param ={
    'params':secretStr,
    'encSecKey':rsaSec,
}

URL = 'http://music.163.com/weapi/search/suggest/web?csrf_token='

r = requests.post(URL,data=param,headers=headers)
print('response status code:',r.status_code)
print(r.text)
