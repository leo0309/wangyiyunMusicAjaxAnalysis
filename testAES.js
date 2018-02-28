var CryptoJS = require('crypto-js');
a={"s":"测试", "csrf_token":""};
test = JSON.stringify(a);
console.log("明文:",test);
a = CryptoJS.enc.Utf8.parse(test);
d = CryptoJS.enc.Utf8.parse("0102030405060708");
g = CryptoJS.enc.Utf8.parse("0CoJUm6Qyw8W8jud");
console.log('enc Utf8后:',a.toString());
//加密测试
b= CryptoJS.AES.encrypt(a,g,{
    iv:d,
    mode:CryptoJS.mode.CBC
});
console.log("加密后:",b.toString());
//解密测试
dec = CryptoJS.AES.decrypt(b.toString(),g,{
    iv:d,
    mode:CryptoJS.mode.CBC
});
console.log('解密后:',dec.toString(CryptoJS.enc.Utf8));
console.log("-----------------------")
content = 'yNI5RpTqacL7+ml1OEaIUdaBSlkW0CvRfWO8mSD1uPIUwWDcOHUyG1g1ys4Srr20';
console.log('python加密后的密文:',content);
aaa = CryptoJS.AES.decrypt(content,g,{
    iv:d,
    mode:CryptoJS.mode.CBC
});

console.log('python加密后的密文解密后:',aaa.toString(CryptoJS.enc.Utf8));