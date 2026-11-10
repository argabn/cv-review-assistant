// Dependency-free behavioral test of the exported review form handler.
const fs = require('fs');
const vm = require('vm');
const assert = require('assert');
const path = require('path');
const script = fs.readFileSync(path.join(__dirname, '../cvflow/assets/report.js'), 'utf8');
let submit, change, exported;
const field = (key,value) => ({dataset:{key},value});
const record = (values,isNew=false,remove=false) => ({
  querySelector:()=>remove?{checked:true}:null,
  querySelectorAll:()=>Object.entries(values).map(([k,v])=>field(k,v)),
  hasAttribute:()=>isNew,
});
const feedback={textContent:''};
const corrections={hidden:true};
const groups=[{dataset:{field:'skills'},querySelectorAll:()=>[
  record({name:'Python',quote:'Skills: Python, SQL.'}),
  record({name:'Wrong',quote:'Wrong'},false,true),
  record({name:'SQL',quote:'Skills: Python, SQL.'},true),
]},...['education','experience','projects'].map(field=>({dataset:{field},querySelectorAll:()=>[record({name:'',quote:''},true)]}))];
const form={dataset:{candidate:'C-0001'},elements:{reviewer:{value:'Reviewer'},notes:{value:'Checked source'},action:{value:'reviewed'},correct:{checked:true,addEventListener:(_,fn)=>change=fn}},
 querySelector:s=>s==='.corrections'?corrections:feedback,
 querySelectorAll:()=>groups,addEventListener:(_,fn)=>submit=fn};
const context={document:{querySelectorAll:()=>[form],createElement:()=>({click(){}})},
 Blob:class{constructor(parts){exported=JSON.parse(parts[0]);}},URL:{createObjectURL:()=> 'blob:local',revokeObjectURL(){}},setTimeout:fn=>fn()};
vm.runInNewContext(script,context);
change();assert.equal(corrections.hidden,false);
submit({preventDefault(){}});
assert.equal(exported.corrected_facts.skills.length,2);
assert.equal(exported.corrected_facts.skills[1].name,'SQL');
assert.equal(exported.corrected_facts.projects.length,0);
assert.equal(exported.candidate_id,'C-0001');
form.elements.correct.checked=false;submit({preventDefault(){}});
assert.equal(exported.corrected_facts,null);
form.elements.reviewer.value='';submit({preventDefault(){}});
assert.match(feedback.textContent,/reviewer/);
console.log('Review form: add, remove, unchanged export, and required fields passed.');
