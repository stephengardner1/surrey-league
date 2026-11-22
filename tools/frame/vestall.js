const fs=require('fs');const src=fs.readFileSync(process.argv[2],'utf8').split('\n');
let i=src.findIndex(l=>l.startsWith('const getClubVestSvg='));let j=i+1;while(!/^(const|function|\/\/|\/\*) ?/.test(src[j]))j++;
const f=new Function(src.slice(i,j).join('\n')+';return getClubVestSvg;')();
const out={};for(const c of JSON.parse(process.argv[3]))out[c]=f(c);console.log(JSON.stringify(out));
