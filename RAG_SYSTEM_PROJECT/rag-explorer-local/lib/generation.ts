export const MODEL = "gemini-3.5-flash-lite";
export type GenerationSettings = {temperature:number; maxTokens:number};
export type Generation = {text:string; model:string; inputTokens:number|null; outputTokens:number|null; latencyMs:number; finishReason:string; estimatedUsd:number|null};
export type GenerationErrorCode = "google_auth"|"model_access"|"quota"|"network"|"timeout"|"provider"|"empty_response";
export class GenerationError extends Error {
 readonly code:GenerationErrorCode;
 readonly httpStatus:number|null;
 constructor(code:GenerationErrorCode,httpStatus:number|null,message:string){super(message);this.name="GenerationError";this.code=code;this.httpStatus=httpStatus;}
}
export function validateGeneration(s:GenerationSettings){
 if(!s || !Number.isFinite(s.temperature)||s.temperature<0||s.temperature>1||!Number.isInteger(s.maxTokens)||s.maxTokens<128||s.maxTokens>1024)throw Error("생성 설정 범위를 확인하세요.");
}
export async function generate(apiKey:string,system:string,context:string,query:string,settings:GenerationSettings,request:typeof fetch=fetch):Promise<Generation>{
 validateGeneration(settings);
 const started=Date.now();
 let response:Response;
 try{response=await request(`https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`,{
  method:"POST",headers:{"Content-Type":"application/json","x-goog-api-key":apiKey},signal:AbortSignal.timeout(45000),
    body:JSON.stringify({systemInstruction:{parts:[{text:system||"근거를 참고해 질문에 답하세요."}]},contents:[{role:"user",parts:[{text:`CONTEXT\n${context||"(검색된 근거 없음)"}\n\nQUESTION\n${query}`}]}],generationConfig:{temperature:settings.temperature,maxOutputTokens:settings.maxTokens}})
 });}catch(error){
  if(error instanceof DOMException&&error.name==="TimeoutError")throw new GenerationError("timeout",null,"Google 요청 시간이 초과되었습니다.");
  throw new GenerationError("network",null,"Google 서비스에 연결하지 못했습니다.");
 }
 if(!response.ok){
  const code=response.status===401||response.status===403?"google_auth":response.status===404?"model_access":response.status===429?"quota":response.status>=400&&response.status<500?"provider":"network";
  const message=code==="google_auth"?"Google 인증 또는 API 키 권한을 확인하세요.":code==="model_access"?"현재 계정에서 이 Gemini 모델에 접근할 수 없습니다.":code==="quota"?"Google 할당량 또는 속도 제한에 도달했습니다.":code==="provider"?"Google이 요청을 거부했습니다. 입력과 생성 설정을 확인하세요.":"Google 서비스 요청에 실패했습니다.";
  throw new GenerationError(code,response.status,message);
 }
 const data=await response.json() as {candidates?:{content?:{parts?:{text?:string;thought?:boolean}[]};finishReason?:string}[];usageMetadata?:{promptTokenCount?:number;candidatesTokenCount?:number}};
 const candidate=data.candidates?.[0];
 const text=candidate?.content?.parts?.filter(p=>!p.thought).map(p=>p.text||"").join("").trim();
 if(!text)throw new GenerationError("empty_response",null,"Google이 텍스트 답변을 반환하지 않았습니다.");
 const inputTokens=data.usageMetadata?.promptTokenCount??null,outputTokens=data.usageMetadata?.candidatesTokenCount??null;
 return {text,model:MODEL,inputTokens,outputTokens,latencyMs:Date.now()-started,finishReason:candidate?.finishReason||"UNKNOWN",estimatedUsd:inputTokens===null||outputTokens===null?null:(inputTokens*.10+outputTokens*.40)/1e6};
}
