import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import ts from 'typescript';
import {DEFAULT_CONFIG} from '../lib/rag-engine.ts';
const source=readFileSync(new URL('../lib/workspace-draft.ts',import.meta.url),'utf8')
 .replace('"./rag-engine"',JSON.stringify(new URL('../lib/rag-engine.ts',import.meta.url).href))
 .replace('"./generation"',JSON.stringify(new URL('../lib/generation.ts',import.meta.url).href));
const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText;
const {parseDraft,serializeDraft}=await import('data:text/javascript;base64,'+Buffer.from(js).toString('base64'));
const input={query:'현재 질문',document:'현재 문서',system:'근거로 답변',config:DEFAULT_CONFIG,settings:{temperature:0,maxTokens:512}};
const draft={input,baseline:{...input,query:'이전 질문',config:{...DEFAULT_CONFIG,topK:1}}};
assert.deepEqual(parseDraft(serializeDraft(draft)),draft);
assert.equal(parseDraft(null),null);
assert.equal(parseDraft('{broken'),null);
assert.equal(parseDraft(JSON.stringify({...draft,version:1,savedAt:Date.now()-86400001})),null);
assert.equal(parseDraft(JSON.stringify({...draft,version:2,savedAt:Date.now()})),null);
assert.equal(parseDraft(serializeDraft({...draft,input:{...input,config:{...DEFAULT_CONFIG,size:0}}})),null);
assert.equal(parseDraft(serializeDraft({...draft,baseline:{...input,settings:{temperature:0,maxTokens:99999}}})),null);
console.log('PASS: distinct A/B drafts restore; expired, malformed and invalid drafts rejected.');
