import {getChatGPTUser} from '@/app/chatgpt-auth';
import {clearKey,connection,modelKey,verifyKey} from '@/lib/key-vault';
import {GenerationError} from '@/lib/generation';
export const dynamic='force-dynamic';
export const runtime='nodejs';
const reply=(data:object,status=200)=>Response.json(data,{status,headers:{'Cache-Control':'no-store'}});
export async function GET(){const u=await getChatGPTUser();if(!u)return reply({error:'localhost 주소로 접속하세요.',code:'local_only'},403);try{return reply(await connection(u.userId));}catch{return reply({error:'연결 상태를 확인하지 못했습니다.',code:'status_unavailable'},503);}}
export async function POST(request:Request){
 const u=await getChatGPTUser();if(!u)return reply({error:'허용되지 않은 요청입니다.'},403);
 if(!request.headers.get('content-type')?.includes('application/json'))return reply({error:'JSON 요청이 필요합니다.'},400);
 try{const raw=await request.text();if(raw.length>200)return reply({error:'요청이 너무 큽니다.'},413);
  const b=JSON.parse(raw);if('key' in b||'apiKey' in b)return reply({error:'키는 서버 .env에서만 읽습니다.'},400);
  if(b.action==='clear'){clearKey();return reply({source:'none',configured:false,verified:false,registrationAvailable:false,cleared:true});}
  if(b.action!=='verify')return reply({error:'지원하지 않는 연결 작업입니다.',code:'invalid_action'},400);
    const key=await modelKey(u.userId);if(!key)return reply({error:'.env에 GOOGLE_API_KEY를 설정하고 서버를 재시작하세요.',code:'key_missing'},400);
  await verifyKey(key);return reply({...await connection(u.userId),verified:true});
 }catch(e){if(e instanceof GenerationError)return reply({error:e.message,code:e.code,httpStatus:e.httpStatus},e.httpStatus&&e.httpStatus>=400&&e.httpStatus<500?e.httpStatus:502);return reply({error:'연결을 확인하지 못했습니다. 네트워크 상태를 확인하세요.',code:'network'},502);}
}
