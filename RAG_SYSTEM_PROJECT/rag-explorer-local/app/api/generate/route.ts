import {getChatGPTUser} from "@/app/chatgpt-auth";
import {generate,GenerationError} from "@/lib/generation";
import {database,saveExperiment,validateInput} from "@/lib/experiment-store";
import {modelKey} from "@/lib/key-vault";
export const dynamic="force-dynamic";
const reply=(b:object,status=200)=>Response.json(b,{status,headers:{"Cache-Control":"no-store"}});
export async function POST(request:Request){
 const user=await getChatGPTUser();if(!user)return reply({error:"로그인 후 다시 시도하세요."},401);
 if(request.headers.get("sec-fetch-site")==="cross-site"||!request.headers.get("content-type")?.includes("application/json"))return reply({error:"허용되지 않은 요청입니다."},403);
 let id:string|undefined;
 try{
  const raw=await request.text();if(raw.length>50000)return reply({error:"입력이 너무 큽니다."},413);
  const b=JSON.parse(raw);if("apiKey" in b)return reply({error:"브라우저에서 API 키를 받지 않습니다."},400);
    const r=validateInput(b);if(!r.query.trim()||!r.document.trim())return reply({error:"질문과 원문을 입력하세요.",code:"invalid_input"},400);
  const saved=await saveExperiment(user.userId,b),db=database();
  const existing=await db.prepare("SELECT status,output FROM runs WHERE id=? AND owner=?").bind(saved.id,user.userId).first<{status:string;output:string|null}>();
  if(existing?.status==="complete"&&existing.output)return reply({...JSON.parse(existing.output),cached:true});
    const confirmUnknown=b.confirmUnknown===true;
    if(existing?.status==="pending")return reply({error:"동일 요청이 이미 처리 중입니다.",code:"pending"},409);
    if(existing?.status==="unknown"&&!confirmUnknown)return reply({error:"이전 요청 결과가 불확실합니다. 이미 과금됐을 수 있습니다. Google 사용 내역을 확인한 뒤 재시도를 확인하세요.",code:"unknown_confirmation_required"},409);
    if(existing&&!["unknown","rejected"].includes(existing.status))return reply({error:"이 요청은 재사용할 수 없는 상태입니다.",code:"invalid_run_state"},409);
  const key=await modelKey(user.userId);if(!key)return reply({error:"프로젝트 .env에 GOOGLE_API_KEY를 설정하고 서버를 재시작하세요. 비용 예상과 통계 저장은 계속 사용할 수 있습니다."},503);
    if(existing){await db.prepare("INSERT INTO run_attempts(attempt_id,run_id,owner,created,status,output,input_tokens,output_tokens,cost) SELECT lower(hex(randomblob(16))),id,owner,created,status,output,input_tokens,output_tokens,cost FROM runs WHERE id=? AND owner=?").bind(saved.id,user.userId).run();}
    const reserved=existing
     ? await db.prepare("UPDATE runs SET created=?,status='pending',output=NULL,input_tokens=NULL,output_tokens=NULL,cost=NULL WHERE id=? AND owner=? AND status IN ('unknown','rejected')").bind(Date.now(),saved.id,user.userId).run()
     : await db.prepare("INSERT INTO runs (id,owner,created,status) SELECT ?,?,?,'pending' WHERE (SELECT COUNT(*) FROM runs WHERE owner=? AND created>=?)<100 ON CONFLICT(id) DO NOTHING").bind(saved.id,user.userId,Date.now(),user.userId,Date.now()-86400000).run();
  if(!reserved.meta.changes)return reply({error:"동일 요청이 진행 중이거나 최근 24시간 100회 호출 한도에 도달했습니다."},429);
  id=saved.id;
  const output=await generate(key,r.system,r.context,r.query,b.settings);
  await db.prepare("UPDATE runs SET status='complete',output=?,input_tokens=?,output_tokens=?,cost=? WHERE id=? AND owner=?").bind(JSON.stringify(output),output.inputTokens,output.outputTokens,output.estimatedUsd,id,user.userId).run();
  return reply({...output,cached:false});
 }catch(error){
  const provider=error instanceof GenerationError;
  const status=provider&&["google_auth","model_access","quota","provider","empty_response"].includes(error.code)?"rejected":"unknown";
  if(id){try{await database().prepare("UPDATE runs SET status=? WHERE id=? AND owner=? AND status='pending'").bind(status,id,user.userId).run();}catch{return reply({error:"생성 결과를 저장하지 못했습니다. 원격 호출 비용은 확인되지 않았습니다.",code:"storage",httpStatus:null},500);}}
  if(provider)return reply({error:error.message,code:error.code,httpStatus:error.httpStatus},error.httpStatus&&error.httpStatus>=400&&error.httpStatus<500?error.httpStatus:502);
  return reply({error:"요청 시간이 초과되었거나 네트워크가 끊겼습니다. 호출이 과금됐을 수 있어 자동 재시도하지 않았습니다.",code:"unknown",httpStatus:null},504);
 }
}
