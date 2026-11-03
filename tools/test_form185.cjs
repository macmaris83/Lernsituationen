const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'master-katalog.json'))).packages;
for(const p of catalog.filter(p=>p.typ==='Lernsituation'||['VORLAGE-TRADIERT','VORLAGE-FUENF-LERNWEGE'].includes(p.id))){
 const result=cp.spawnSync(process.execPath,[path.join(__dirname,'test_idn_completion.cjs')],{env:{...process.env,LS_TEST_MASTER:p.master},encoding:'utf8'});
 assert.equal(result.status,0,p.id+'\n'+result.stderr+'\n'+result.stdout);
 const current=fs.readFileSync(path.join(root,p.master,'progress-meta.js'),'utf8');
 const baseline=cp.execFileSync('git',['show','HEAD:'+p.master+'/progress-meta.js'],{cwd:root,encoding:'utf8'});
 assert.equal(current,baseline,p.id+': persistent task, orientation and quiz signatures must stay unchanged');
 console.log('PASS',p.id,'completion, failures, retry, reopen, unchanged signatures');
}
