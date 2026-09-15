import {localDatabase} from "@/lib/local-db";
import {calculate} from "@/lib/rag-engine";
import {MODEL,validateGeneration} from "@/lib/generation";
import {estimateCost,stableInput,type ExperimentInput} from "@/lib/cost";
export function database(){return localDatabase();}
export function apiKey(){return process.env.GOOGLE_API_KEY?.trim()||"";}
export function validateInput(b:ExperimentInput){
 if(!b||typeof b.query!=="string"||typeof b.document!=="string"||typeof b.system!=="string"||!b.config)throw Error("입력 형식을 확인하세요.");
 validateGeneration(b.settings);return calculate(b.query,b.document,b.system,b.config);
}
export async function fingerprint(owner:string,b:ExperimentInput){
 const digest=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(owner+"/"+MODEL+"/v1/"+stableInput(b)));
 return Array.from(new Uint8Array(digest),v=>v.toString(16).padStart(2,"0")).join("");
}
export async function saveExperiment(owner:string,b:ExperimentInput){
 const r=validateInput(b);
 b={query:r.query,document:r.document,system:r.system,config:{size:r.config.size,overlap:r.config.overlap,topK:r.config.topK,rerank:r.config.rerank,budget:r.config.budget},settings:{temperature:b.settings.temperature,maxTokens:b.settings.maxTokens}};
 const estimate=estimateCost(r,b.settings),id=await fingerprint(owner,b);
 await database().prepare("INSERT INTO experiments (id,owner,created,snapshot,estimate) VALUES (?,?,?,?,?) ON CONFLICT(id) DO NOTHING").bind(id,owner,Date.now(),JSON.stringify(b),JSON.stringify(estimate)).run();
 return {id,estimate};
}
export async function statistics(owner:string){
 const db=database();
 const [records,totals]=await Promise.all([
 db.prepare("SELECT e.id,e.created,e.snapshot,e.estimate,r.status,r.output,r.input_tokens,r.output_tokens,r.cost FROM experiments e LEFT JOIN runs r ON r.id=e.id AND r.owner=e.owner WHERE e.owner=? ORDER BY e.created DESC,e.id DESC LIMIT 50").bind(owner).all(),
 db.prepare("SELECT (SELECT COUNT(*) FROM experiments WHERE owner=?) AS experiments,COUNT(*) AS calls,COALESCE(SUM(CASE WHEN status='complete' THEN 1 ELSE 0 END),0) AS completed,COALESCE(SUM(CASE WHEN status!='complete' THEN 1 ELSE 0 END),0) AS unknown,COALESCE(SUM(input_tokens),0) AS inputTokens,COALESCE(SUM(output_tokens),0) AS outputTokens,COALESCE(SUM(cost),0) AS cost FROM runs WHERE owner=?").bind(owner,owner).first()
 ]);
 return {records:records.results.map(row=>({...row,snapshot:JSON.parse(row.snapshot as string),estimate:JSON.parse(row.estimate as string),output:row.output?JSON.parse(row.output as string):null})),totals};
}
