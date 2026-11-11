const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'master-katalog.json'))).packages;
for(const p of catalog.filter(p=>p.typ==='Lernsituation'||['VORLAGE-TRADIERT','VORLAGE-FUENF-LERNWEGE'].includes(p.id))){
 const result=cp.spawnSync(process.execPath,[path.join(__dirname,'test_idn_completion.cjs')],{env:{...process.env,LS_TEST_MASTER:p.master},encoding:'utf8'});
 assert.equal(result.status,0,p.id+'\n'+result.stderr+'\n'+result.stdout);
 const current=fs.readFileSync(path.join(root,p.master,'progress-meta.js'),'utf8');
 const baseline=cp.execFileSync('git',['show','HEAD:'+p.master+'/progress-meta.js'],{cwd:root,encoding:'utf8'});
 if(p.id==='VORLAGE-FUENF-LERNWEGE'){
  assert.equal(current,baseline,p.id+': five-path template remains unchanged');
 }else{
  const parse=source=>JSON.parse(source.slice(source.indexOf('=')+1).trim().replace(/;$/,''));
  const before=parse(baseline),after=parse(current);
  const w1=Object.fromEntries(Object.entries(before.tasks).filter(([,task])=>task.mode===1));
  assert.deepEqual(after.tasks,w1,p.id+': retain every original W1 ID/signature; remove only other paths');
  for(const field of Object.keys(before).filter(key=>!['tasks','migration','resumePages'].includes(key)))
   assert.deepEqual(after[field],before[field],p.id+': preserve '+field);
  for(const [id,rule] of Object.entries(after.migration?.tasks||{})){
   assert.ok(after.tasks[id]?.mode===1,p.id+': no obsolete task migration');
   assert.deepEqual(rule,before.migration?.tasks?.[id],p.id+': preserve valid W1 migration');
  }
 }
 console.log('PASS',p.id,'completion, failures, retry, reopen, unchanged signatures');
}
