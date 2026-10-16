import test from 'node:test';
import assert from 'node:assert/strict';
import '../dist/calculator.js';
const calc=()=>BioCasaCalculator.create();
const press=(c,text)=>{for(const key of text)c.press(key);return c.view();};
test('Plus und Minus rechnen in Cent und liefern erst nach Bestätigung einen übernehmbaren Wert',()=>{
 const c=calc();press(c,'0,10');assert.equal(c.view().value,null);c.press('+');press(c,'0,20');c.press('equals');assert.equal(c.view().value,30);assert.equal(c.view().display,'0,30');c.press('-');press(c,'1,00');c.press('equals');assert.equal(c.view().value,-70);assert.equal(c.view().display,'-0,70');
});
test('Laufende Summen, Operatorwechsel, Rücktaste und Löschen übernehmen keine versteckten Werte',()=>{
 const c=calc();press(c,'100+20+5-');c.press('+');press(c,'10');c.press('back');press(c,'2');c.press('equals');assert.equal(c.view().value,13700);press(c,'8');assert.equal(c.view().value,null);c.press('clear');assert.equal(c.view().display,'0,00');assert.equal(c.view().expression,'');assert.equal(c.view().value,null);
});
test('Zwei Dezimalstellen, große Beträge und unbekannte Tasten bleiben kontrolliert',()=>{
 const c=calc();press(c,',1234');c.press('equals');assert.equal(c.view().value,12);c.press('clear');press(c,'9999999999,99+1');c.press('equals');assert.ok(c.view().error.includes('zu groß'));assert.equal(c.view().value,null);c.press('clear');c.press('*');assert.equal(c.view().display,'0,00');
});
