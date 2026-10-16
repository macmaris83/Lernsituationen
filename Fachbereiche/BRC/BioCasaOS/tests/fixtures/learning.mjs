import '../../dist/engine.js';
import '../../dist/didactics.js';
import '../../dist/course-config.js';
import '../../dist/release.js';
import '../../dist/inventory-cases.js';
import '../../dist/later-lessons.js';
import '../../dist/learning.js';
export const inventoryAnswers={flour:{quantity:'962,5',value:'1925',method:'physical',ownership:'exclude'},documents:{method:'documents',bank:'160390',loan:'490000',creditLine:'exclude'},pizza:{method:'physical',quantity:'90',value:'270',evidence:'countsheet'},cutoff:{quantity:'335',value:'670',procedure:'rollforward',timing:'stichtag'},permanent:{quantity:'730',timing:'permanent',physicalCheck:'required',axes:'both'}};
export const answers={inventory:inventoryAnswers.flour,inventar:{vehicle:'av',furniture:'av',bank:'uv',loan:'debt',basicAssets:'667390',debts:'490000',equity:'362500'},balance:{bankSide:'assets',loanSide:'passives',leftTotal:'852500',rightTotal:'852500'},accounts:{bankStart:'debit',loanStart:'credit',bankAmount:'160390',loanAmount:'490000',assetIncrease:'debit',debtIncrease:'credit'},income:{expense:'670',amount:'1000',payment:'280',profit:'down',revenueSide:'credit',cash:'same'},tax:{vehicle:'40000',vat:'7600',gross:'47600',outputTax:'190',nature:'claim'},further:{depreciation:'1000',debit:'652',credit:'076',cash:'same',stock:'separate'},returns:{net:'200',vat:'38',gross:'238',cash:'same',stock:'inspect'},accrual:{ara:'600',araSide:'debit',pra:'900',praSide:'credit',period:'next',cash:'same'}};
export const builderAnswers={...answers,
 inventar:{...answers.inventar,schema:'2',...Object.fromEntries(BioCasaDidactics.POSITIONS.map(r=>[r.field,r.kind]))},
 balance:{...answers.balance,schema:'2',equitySide:'passives',...Object.fromEntries(BioCasaDidactics.POSITIONS.map(r=>[r.sideField,r.kind==='debt'?'passives':'assets']))},
 accounts:{...answers.accounts,schema:'2',...BioCasaDidactics.decisionAnswers('accounts')},
 income:{...answers.income,schema:'2',...BioCasaDidactics.decisionAnswers('income')}
};
export function builderComplete(state=BioCasa.newState()){state=inventoryDone(state);for(const step of BioCasaLearning.STEPS.slice(1))state=BioCasaLearning.record(state,step.id,builderAnswers[step.id]).state;return state;}
export function inventoryDone(state=BioCasa.newState()){for(const [id,a] of Object.entries(inventoryAnswers))state=BioCasaLearning.recordInventory(state,id,a).state;return state;}
export function foundations(state=BioCasa.newState()){state=inventoryDone(state);for(const step of BioCasaLearning.STEPS.slice(1,4))state=BioCasaLearning.record(state,step.id,answers[step.id]).state;return state;}
export function complete(state=foundations()){for(const step of BioCasaLearning.STEPS.slice(4))state=BioCasaLearning.record(state,step.id,answers[step.id]).state;return state;}
