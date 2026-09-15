import {apiKey} from '@/lib/experiment-store';
import {GenerationError,MODEL} from '@/lib/generation';
const state=globalThis as typeof globalThis&{geminiConnection?:{verifiedAt:number}};
function verified(){return !!apiKey()&&!!state.geminiConnection?.verifiedAt;}
export async function connection(_owner:string){return {source:apiKey()?'environment':'none',configured:!!apiKey(),verified:verified(),verifiedAt:verified()?state.geminiConnection?.verifiedAt??null:null,registrationAvailable:false};}
export async function modelKey(_owner:string){return apiKey();}
export function clearKey(){delete process.env.GOOGLE_API_KEY;delete state.geminiConnection;}
export async function verifyKey(key:string){
 const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL}`,{headers:{'x-goog-api-key':key},signal:AbortSignal.timeout(12000)});
 if(!r.ok){const code=r.status===401||r.status===403?'google_auth':r.status===404?'model_access':r.status===429?'quota':'provider';throw new GenerationError(code,r.status,'Google 모델 조회에 실패했습니다.');}
 const m=await r.json() as {supportedGenerationMethods?:string[]};if(!m.supportedGenerationMethods?.includes('generateContent'))throw new GenerationError('model_access',null,'모델의 생성 권한을 확인하지 못했습니다.');
 state.geminiConnection={verifiedAt:Date.now()};
}
