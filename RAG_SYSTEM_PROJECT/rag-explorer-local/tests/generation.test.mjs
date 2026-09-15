import assert from 'node:assert/strict';
import {generate,validateGeneration,MODEL} from '../lib/generation.ts';
import {calculate,DEFAULT_QUERY,DEFAULT_DOCUMENT,DEFAULT_SYSTEM,DEFAULT_CONFIG} from '../lib/rag-engine.ts';
const settings={temperature:0,maxTokens:512};
let calls=[];
const mock=async(url,options)=>{
 calls.push({url,options,body:JSON.parse(options.body)});
 return Response.json({candidates:[{content:{parts:[{text:'hidden',thought:true},{text:'답변 [C01]'}]},finishReason:'STOP'}],usageMetadata:{promptTokenCount:2000,candidatesTokenCount:500}});
};
const a=calculate(DEFAULT_QUERY,DEFAULT_DOCUMENT,DEFAULT_SYSTEM,DEFAULT_CONFIG);
const b=calculate('식비는 얼마인가요?',DEFAULT_DOCUMENT,'두 줄로 답하세요.',{...DEFAULT_CONFIG,topK:1});
const answer=await generate('test-key',a.system,a.context,a.query,settings,mock);
await generate('test-key',b.system,b.context,b.query,settings,mock);
assert.equal(answer.text,'답변 [C01]');assert.equal(answer.estimatedUsd,.0004);
assert.equal(calls.length,2);assert.ok(calls[0].url.includes(MODEL));assert.ok(!calls[0].url.includes('test-key'));
assert.equal(calls[0].options.headers['x-goog-api-key'],'test-key');
assert.equal(calls[1].body.systemInstruction.parts[0].text,b.system);
assert.equal(calls[1].body.contents[0].parts[0].text,`CONTEXT\n${b.context}\n\nQUESTION\n${b.query}`);
assert.notEqual(calls[0].body.contents[0].parts[0].text,calls[1].body.contents[0].parts[0].text);
assert.equal(calls[0].body.generationConfig.thinkingConfig,undefined);
for(const invalid of [{temperature:-1,maxTokens:512},{temperature:0,maxTokens:10000},{temperature:NaN,maxTokens:512}])assert.throws(()=>validateGeneration(invalid));
for(const [status,code] of [[400,'provider'],[403,'google_auth'],[429,'quota']]){
 await assert.rejects(()=>generate('key','','','q',settings,async()=>new Response('secret provider diagnostic',{status})),e=>e.code===code&&e.httpStatus===status);
}
await assert.rejects(()=>generate('key','','','q',settings,async()=>new Response('secret provider diagnostic',{status:403})),/API 키/);
await assert.rejects(()=>generate('key','','','q',settings,async()=>{throw new DOMException('timed out','TimeoutError')}),e=>e.code==='timeout');
await assert.rejects(()=>generate('key','','','q',settings,async()=>Response.json({candidates:[]})),/텍스트/);
console.log('Generation adapter: A/B prompt mapping, bounded settings, usage, secret-safe errors and empty responses passed (mock provider; no paid calls).');
