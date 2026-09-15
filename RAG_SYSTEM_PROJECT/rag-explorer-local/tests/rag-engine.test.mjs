import assert from "node:assert/strict";
import {calculate,chunkDocument,validateConfig,DEFAULT_CONFIG,DEFAULT_QUERY,DEFAULT_DOCUMENT,DEFAULT_SYSTEM} from "../lib/rag-engine.ts";
const run=(patch={})=>calculate(DEFAULT_QUERY,DEFAULT_DOCUMENT,DEFAULT_SYSTEM,{...DEFAULT_CONFIG,...patch});
const baseline=run();
const tiny=run({size:60,overlap:10});
assert.notEqual(baseline.chunks.length,tiny.chunks.length);
assert.notEqual(baseline.answer,tiny.answer);
assert.notEqual(baseline.prompt,tiny.prompt);
assert.notDeepEqual(run({overlap:0}).chunks,run({overlap:50}).chunks);
assert.equal(run({topK:1}).candidates.length,1);
assert.notEqual(run({topK:1}).answer,run({topK:5,budget:1200}).answer);
assert.ok(run({budget:200}).selected.length<baseline.selected.length);
assert.notDeepEqual(run({size:60,overlap:0,rerank:false}).selected.map(c=>c.id),run({size:60,overlap:0,rerank:true}).selected.map(c=>c.id));
assert.equal(calculate("zzzzzz",DEFAULT_DOCUMENT,DEFAULT_SYSTEM,DEFAULT_CONFIG).selected.length,0);
assert.equal(calculate(DEFAULT_QUERY,"",DEFAULT_SYSTEM,DEFAULT_CONFIG).chunks.length,0);
assert.equal(calculate("",DEFAULT_DOCUMENT,DEFAULT_SYSTEM,DEFAULT_CONFIG).candidates.length,0);
assert.throws(()=>validateConfig({...DEFAULT_CONFIG,size:NaN}));
assert.throws(()=>validateConfig({...DEFAULT_CONFIG,overlap:180}));
assert.throws(()=>chunkDocument("hello",3,3));
for(const size of [60,180,400])for(const overlap of [0,10,50])for(const topK of [1,3,8])for(const budget of [200,650,1600]){
 const r=run({size,overlap,topK,budget});
 assert.ok(r.used<=budget);
 assert.ok(r.selected.length<=topK);
 assert.ok(r.selected.every(c=>r.candidates.some(x=>x.id===c.id)));
 for(const c of r.chunks){assert.equal(c.text,DEFAULT_DOCUMENT.slice(c.start,c.end));assert.ok(c.text.length<=size)}
 assert.equal(r.chunks.at(-1).end,DEFAULT_DOCUMENT.length);
 for(const e of r.evidence){const c=r.selected.find(c=>c.id===e.id);assert.ok(c.text.includes(e.text));assert.equal(DEFAULT_DOCUMENT.slice(e.start,e.end),e.text)}
 assert.ok(r.prompt.endsWith(DEFAULT_QUERY));
 assert.ok(r.chunks.every(c=>c.score>=0&&c.score<=1.000001));
}
const changedSystem=calculate(DEFAULT_QUERY,DEFAULT_DOCUMENT,"새 지시문",DEFAULT_CONFIG);
assert.ok(changedSystem.prompt.includes("새 지시문"));
assert.equal(changedSystem.answer,baseline.answer);
console.log("PASS: 81 parameter combinations, evidence lineage, reranking, budget, empty input, query, prompt, validation.");
