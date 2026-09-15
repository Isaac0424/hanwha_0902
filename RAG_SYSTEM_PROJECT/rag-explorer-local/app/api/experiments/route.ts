import {getChatGPTUser} from "@/app/chatgpt-auth";
import {apiKey,database,saveExperiment,statistics} from "@/lib/experiment-store";
import {connection} from "@/lib/key-vault";
export const dynamic="force-dynamic";
const reply=(b:object,status=200)=>Response.json(b,{status,headers:{"Cache-Control":"no-store"}});
export async function GET(){
 const u=await getChatGPTUser();if(!u)return reply({error:"로그인이 필요합니다."},401);
 try{return reply({...await statistics(u.userId),configured:(await connection(u.userId)).configured});}catch{return reply({error:"통계를 불러오지 못했습니다. 잠시 후 새로고침하세요."},503);}
}
export async function POST(req:Request){
 const u=await getChatGPTUser();if(!u)return reply({error:"로그인이 필요합니다."},401);
 if(req.headers.get("sec-fetch-site")==="cross-site"||!req.headers.get("content-type")?.includes("application/json"))return reply({error:"허용되지 않은 요청입니다."},403);
 try{const raw=await req.text();if(raw.length>50000)return reply({error:"입력이 너무 큽니다."},413);
  const saved=await saveExperiment(u.userId,JSON.parse(raw));return reply(saved);
 }catch{return reply({error:"설정 기록을 저장하지 못했습니다. 입력 범위를 확인하고 다시 저장하세요."},503);}
}
export async function DELETE(req:Request){
 const u=await getChatGPTUser();if(!u)return reply({error:"로그인이 필요합니다."},401);
 if(req.headers.get("sec-fetch-site")==="cross-site"||!req.headers.get("content-type")?.includes("application/json"))return reply({error:"허용되지 않은 요청입니다."},403);
 try{const raw=await req.text();if(raw.length>10000)return reply({error:"삭제 요청이 너무 큽니다."},413);const body=JSON.parse(raw) as {ids?:unknown};const ids=Array.isArray(body.ids)?body.ids.filter((id):id is string=>typeof id==='string'&&/^[a-f0-9]{64}$/.test(id)):[];if(!ids.length)return reply({error:"삭제할 실험을 선택하세요.",code:"invalid_selection"},400);const db=database();let deleted=0;for(const id of ids){const owned=await db.prepare("SELECT id FROM experiments WHERE id=? AND owner=?").bind(id,u.userId).first();if(!owned)continue;await db.prepare("DELETE FROM run_attempts WHERE run_id=? AND owner=?").bind(id,u.userId).run();await db.prepare("DELETE FROM runs WHERE id=? AND owner=?").bind(id,u.userId).run();deleted+=Number((await db.prepare("DELETE FROM experiments WHERE id=? AND owner=?").bind(id,u.userId).run()).meta.changes);}return reply({deleted});}catch{return reply({error:"실험 기록을 삭제하지 못했습니다.",code:"storage"},500);}
}
