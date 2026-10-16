const {test}=require('node:test');
const assert=require('node:assert/strict');
const {Calculator}=require('../Komponenten/Rechner/calculator-engine.js');
function calculate(keys){const c=new Calculator();for(const key of keys)c.press(key);return c;}
test('four operators and normal precedence',()=>{
 for(const [keys,result]of [['12+34=','46'],['9-15=','-6'],['12*5=','60'],['12/5=','2,4'],['2+3*4=','14'],['18/3*2-1=','11']])assert.equal(calculate(keys).display,result);
});
test('decimal comma and float presentation',()=>{
 assert.equal(calculate('0,1+0,2=').display,'0,3');assert.equal(calculate('19,95*3=').display,'59,85');assert.equal(calculate('1/3=').display,'0,33333333333333');
});
test('percent alone, markup, discount, multiplication and division',()=>{
 for(const [keys,result]of [['10%','0,1'],['200+10%=','220'],['200-15%=','170'],['200*10%=','20'],['200/10%=','2000'],['200+10%+10%=','242']])assert.equal(calculate(keys).display,result);
});
test('sign, clear, correction and repeated equals',()=>{
 assert.equal(calculate(['5','±','*','2','=']).display,'-10');assert.equal(calculate(['1','2','Backspace','3']).display,'13');assert.equal(calculate(['9','AC','2','+','3','=','=']).display,'8');assert.equal(calculate('2+*3=').display,'6');
});
test('division by zero recovers using the next number',()=>{
 const c=calculate('5/0=');assert.equal(c.display,'Fehler');assert.equal(c.error,'Division durch null');c.press('7');assert.equal(c.display,'7');
});
test('page change restores a pending calculation',()=>{
 const a=calculate('200+10%');const b=new Calculator(JSON.parse(JSON.stringify(a.snapshot())));b.press('=');assert.equal(b.display,'220');
});
test('damaged persisted data cannot introduce operators or code',()=>{
 const c=new Calculator({entry:'123',tokens:[5,'**']});assert.equal(c.display,'0');const d=new Calculator({entry:'alert(1)',tokens:[]});assert.equal(d.display,'0');
});
