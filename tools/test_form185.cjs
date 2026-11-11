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
  if(JSON.stringify(after.tasks)!==JSON.stringify(w1)){
   const report=JSON.parse(fs.readFileSync(path.join(root,'tools/fixtures/task-slimming-report.json'),'utf8'));
   const change=report.packages.find(item=>item.id===p.id);
   assert.ok(change,p.id+': changed task groups require an explicit migration report');
   assert.deepEqual(change.beforeMeta.tasks,before.tasks,p.id+': grouping starts at the checked-in task metadata');
   assert.deepEqual(change.afterMeta.tasks,after.tasks,p.id+': grouping produces exactly the reported task metadata');
   assert.deepEqual(change.afterMeta.migration,after.migration,p.id+': retain the reported AND migration rules');
  }
  for(const field of Object.keys(before).filter(key=>!['tasks','migration','resumePages','legacyTaskDictionaries'].includes(key))){
   if(field==='orientationSignature'&&after[field]!==before[field]){
    assert.equal(p.id,'BRC-LG01-LS05','only the requested orientation title changes its signature');
    assert.equal(after[field],'0b943fa7',p.id+': framed-title signature');
    assert.equal(after.migration.orientationSignature,after[field],p.id+': guarded orientation migration');
    assert.ok(after.migration.orientationSignatures.includes(before[field]),p.id+': previous orientation stays read');
   }else assert.deepEqual(after[field],before[field],p.id+': preserve '+field);
  }
  for(const [id,rule] of Object.entries(after.migration?.tasks||{})){
   assert.ok(after.tasks[id]?.mode===1,p.id+': no obsolete task migration');
   assert.equal(rule.signature,after.tasks[id].signature,p.id+': migration targets the current group signature');
   assert.ok(rule.from.length>0&&rule.from.every(old=>/^\d+:1:\d+$/.test(old.id)),p.id+': preserve W1-only constituent requirements');
  }

 }
 console.log('PASS',p.id,'100 XP, completion, failures, retry, reopen, explicit task migration, preserved content metadata');
}
