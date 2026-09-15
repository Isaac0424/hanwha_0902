"use client";
import {useEffect,useRef,useState,useCallback} from "react";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Table,TableBody,TableCell,TableHead,TableHeader,TableRow} from "@/components/ui/table";
import {MODEL,type Generation,type GenerationSettings} from "@/lib/generation";
import {estimateCost,experimentInput,stableInput,type ExperimentInput} from "@/lib/cost";
import type {Result} from "@/lib/rag-engine";
type Output=Generation&{cached?:boolean};
type Saved={result:Result;settings:GenerationSettings;output:Output};
type RecordRow={id:string;created:number;snapshot:ExperimentInput;estimate:ReturnType<typeof estimateCost>;status:string|null;output:Generation|null;input_tokens:number|null;output_tokens:number|null;cost:number|null};
type Stats={records:RecordRow[];configured:boolean;totals:{experiments:number;calls:number;completed:number;unknown:number;inputTokens:number;outputTokens:number;cost:number}};
const usd=(n:number)=>`$${n.toFixed(6)}`;
export function GenerationLab({a,b,onLoad}:{a:Result;b:Result;onLoad:(input:ExperimentInput)=>void}){
 const [settings,setSettings]=useState<GenerationSettings>({temperature:0,maxTokens:512});
 const [answers,setAnswers]=useState<{A?:Saved;B?:Saved}>({}),[busy,setBusy]=useState<string|null>(null),[error,setError]=useState(""),[unknownTarget,setUnknownTarget]=useState<"A"|"B"|null>(null);
 const [stats,setStats]=useState<Stats|null>(null),[saveState,setSaveState]=useState("저장 대기"),[retry,setRetry]=useState(0);
 const lock=useRef(false);
 const input=experimentInput(b,settings),signature=stableInput(input);
 const valid=Number.isInteger(settings.maxTokens)&&settings.maxTokens>=128&&settings.maxTokens<=1024;
 const refresh=useCallback(async()=>{const response=await fetch("/api/experiments",{cache:"no-store"});const data=await response.json() as Stats&{error?:string};if(!response.ok)throw Error(data.error||"통계 로드 실패");setStats(data);},[]);
 useEffect(()=>{refresh().catch(()=>setSaveState("통계 연결 실패 · 다시 저장을 눌러주세요."));},[refresh]);
 useEffect(()=>{
  if(!valid){setSaveState("출력 토큰 범위를 확인하세요.");return;}
  let active=true;setSaveState("변경 중 · 잠시 멈추면 자동 저장");
  const timer=setTimeout(async()=>{try{
   const response=await fetch("/api/experiments",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(input)});
   if(!response.ok)throw Error("저장 실패");
   if(active){setSaveState("저장 완료 · 동일 입력·설정은 한 기록으로 유지");await refresh();}
  }catch{if(active)setSaveState("저장 실패 · 입력은 유지됩니다. 다시 저장하세요.");}},800);
  return()=>{active=false;clearTimeout(timer)};
  // The canonical signature covers all input and configuration fields.
  // eslint-disable-next-line react-hooks/exhaustive-deps
 },[signature,valid,retry,refresh]);
 async function run(targets:("A"|"B")[],confirmUnknown=false){
  if(lock.current)return;lock.current=true;setError("");setBusy(targets.join(" / "));
  const snapshot={A:a,B:b},captured={...settings};
  try{for(const target of targets){const result=snapshot[target];
    const response=await fetch("/api/generate",{method:"POST",headers:{"Content-Type":"application/json"},signal:AbortSignal.timeout(55000),body:JSON.stringify({...experimentInput(result,captured),...(confirmUnknown?{confirmUnknown:true}:{})})});
    const output=await response.json() as Output&{error?:string;code?:string};if(!response.ok){if(output.code==="unknown_confirmation_required")setUnknownTarget(target);throw Error(output.error||"생성 실패");}
   setAnswers(previous=>({...previous,[target]:{result,settings:captured,output}}));
  }}catch(e){setError(e instanceof Error?e.name==="TimeoutError"?"시간 초과 · 처리 결과와 비용은 미확인 상태일 수 있습니다. 자동 재호출하지 않습니다.":e.message:"연결 오류");}finally{lock.current=false;setBusy(null);refresh().catch(()=>setSaveState("통계 갱신 실패 · 다시 저장을 눌러주세요."));}
 }
 function load(row:RecordRow){setSettings(row.snapshot.settings);onLoad(row.snapshot);}
 const estimates={A:estimateCost(a,settings),B:estimateCost(b,settings)};
 return <section className="panel generation-panel" id="generation"><p className="eyebrow">COST LAB / NO INFERENCE REQUIRED</p><h2>추론 전에 비용부터 비교하세요</h2><p className="muted">설정 변경 → 무료 예상 계산 → 통계 저장. 답변 생성 버튼을 눌러야 모델을 호출합니다. 동일 입력·설정의 저장된 답변은 재사용합니다.</p>
  <div className="cost-cards"><article><small>지금 설정 변경의 LLM 비용</small><strong>$0</strong><span>외부 토큰 계산·임베딩·추론 호출 없음</span></article>{(["A","B"] as const).map(t=><article key={t}><small>{t} · 생성 시 예상 예산</small><strong>{valid?usd(estimates[t].totalUsd):"범위 확인"}</strong><span>입력 약 {estimates[t].inputTokens}토큰 · prompt {estimates[t].promptChars}자 · context {estimates[t].contextChars}자</span><span>출력 최대 {settings.maxTokens}토큰은 설정 고정</span><span>입력 {usd(estimates[t].inputUsd)} / 출력 예산 {usd(estimates[t].outputBudgetUsd)}</span></article>)}</div>
  <p className="muted">입력 추정식: 프롬프트 문자 수÷3 + 역할 구분 여유 16토큰. 모델 토크나이저 실측이 아니며 언어·서식에 따라 오차가 있습니다. 출력은 설정 한도를 모두 사용한다고 가정한 예산입니다. 실제 청구액이나 엄밀한 최대 비용은 아닙니다. 검색·임베딩은 현재 로컬 계산이라 API 비용 $0입니다.</p>
  <div className="generation-controls"><div><label>서버 연결 상태</label><p className="model-name">{stats?stats.configured?"서버 키 등록됨":"서버 키 미등록":"상태 확인 중"}</p><small>GOOGLE_API_KEY · 서버 전용 비밀 환경변수<br/>브라우저는 키를 입력·보관·전송하지 않습니다.</small></div><div><label>연결 모델</label><p className="model-name">{MODEL}</p><small>100만 토큰당 입력 $0.10 / 출력 $0.40<br/>단가 기준: 2026-09-14 · USD</small></div><div><label htmlFor="temperature">Temperature</label><Input id="temperature" type="number" min={0} max={1} step={.1} value={settings.temperature} onChange={e=>setSettings(s=>({...s,temperature:Math.max(0,Math.min(1,Number(e.target.value)))}))}/><small>답변 변화에 영향 · 추정 토큰은 동일</small></div><div><label htmlFor="output-limit">최대 출력 토큰</label><Input id="output-limit" type="number" min={128} max={1024} step={128} value={settings.maxTokens} onChange={e=>setSettings(s=>({...s,maxTokens:Number(e.target.value)}))}/><small>128–1,024 · 출력 예산에 반영</small></div></div>
  <p className="muted">비공개 서버에 입력·RAG 설정·생성 설정·예상치·응답·사용량을 저장합니다. 입력 변경을 0.8초 멈추면 B를 저장하고, A는 생성 시 저장합니다. <a href="https://ai.google.dev/gemini-api/docs/pricing" target="_blank" rel="noreferrer">공식 요금·데이터 이용 정책</a></p>
  <div className="generation-actions"><span role="status">{saveState}</span><Button variant="outline" size="sm" onClick={()=>setRetry(v=>v+1)}>다시 저장 / 통계 갱신</Button></div>
  <div className="generation-actions">{(["A","B"] as const).map(t=><Button key={t} variant="outline" disabled={!!busy||!valid} onClick={()=>run([t])}>{t} 답변 생성 / 재사용</Button>)}<Button disabled={!!busy||!valid} onClick={()=>run(["A","B"])}>A/B 답변 비교 · 최대 2회 호출</Button><span role="status">{busy?`${busy} 처리 중…`:"수동 실행 · 동일 요청 중복 차단 · 최근 24시간 최대 100회"}</span></div>
    {error&&<p className="compare-warning" role="alert">{error}{unknownTarget&&<><br/><Button size="sm" variant="outline" disabled={!!busy} onClick={()=>{const target=unknownTarget;setUnknownTarget(null);void run([target],true)}}>비용 확인 후 재시도</Button></>}</p>}
  <div className="comparison-grid">{(["A","B"] as const).map(t=>{const saved=answers[t],current=t==="A"?a:b;const stale=saved&&stableInput(experimentInput(saved.result,saved.settings))!==stableInput(experimentInput(current,settings));return <article key={t} className={`snapshot snapshot-${t.toLowerCase()}`}><h3>{t} · LLM 생성 답변</h3>{saved?<><p className={stale?"compare-warning":"muted"}>{stale?"이전 입력·설정의 결과입니다. 다시 실행하면 현재 설정의 결과를 확인합니다.":saved.output.cached?"저장된 답변 재사용 · 이번 LLM 비용 $0":"현재 입력·설정으로 생성한 답변"}</p><p className="snapshot-query">{saved.result.query}</p><p className="generated-text">{saved.output.text}</p>{saved.output.finishReason==="MAX_TOKENS"&&<p className="compare-warning">출력 한도에 도달해 답변이 잘렸습니다.</p>}<small>원 실행 입력 {saved.output.inputTokens??"미제공"} / 출력 {saved.output.outputTokens??"미제공"} 토큰 · {(saved.output.latencyMs/1000).toFixed(2)}초 · {saved.output.estimatedUsd===null?"비용 미확인":`유료 단가 환산 ${usd(saved.output.estimatedUsd)}`}</small><details><summary>실제로 전송된 RAG 근거 보기 · {saved.result.selected.length}개 청크</summary><pre className="data-code">{saved.result.context||"선택된 근거 없음"}</pre></details><details><summary>이 답변의 최종 프롬프트</summary><pre className="data-code">{saved.result.prompt}</pre></details></>:<p className="empty-copy">추론 없이 위 예상 비용과 아래 통계부터 비교할 수 있습니다.</p>}</article>})}</div>
  <h2 className="stats-heading">저장된 실험과 비용 통계</h2>{stats?<><div className="cost-cards"><article><small>저장된 입력·설정 조합</small><strong>{stats.totals.experiments}개</strong><span>예상치 기록 · 추론 없이도 저장</span></article><article><small>확인된 생성 / 전체 호출 시작</small><strong>{stats.totals.completed} / {stats.totals.calls}</strong><span>미확인·처리 중 {stats.totals.unknown}회</span></article><article><small>확인된 사용량의 유료 단가 환산</small><strong>{usd(stats.totals.cost)}</strong><span>입력 {stats.totals.inputTokens} / 출력 {stats.totals.outputTokens} 토큰</span></article></div><p className="muted">예상 비용은 실제 지출 합계에 더하지 않습니다. 미확인 호출의 비용은 합계에 포함되지 않습니다. 무료 할당량·세금·사업자 청구서는 반영하지 않습니다.</p>
  <div className="cost-chart" aria-label="최근 12개 설정의 생성 예상 비용">{stats.records.slice(0,12).reverse().map((row,i)=><div key={row.id}><span>#{i+1} · K {row.snapshot.config.topK}</span><i style={{width:`${Math.max(2,row.estimate.totalUsd/Math.max(...stats.records.slice(0,12).map(r=>r.estimate.totalUsd),.000001)*65)}%`}}/><small>{usd(row.estimate.totalUsd)}</small></div>)}</div>
  <div className="stats-table"><Table><TableHeader><TableRow><TableHead>저장 시각 / 질문</TableHead><TableHead>Size / Overlap / K / 예산</TableHead><TableHead>예상 입력 / 출력 한도</TableHead><TableHead>생성 예상 예산</TableHead><TableHead>실제 사용 / 환산 비용</TableHead><TableHead>입력·결과</TableHead></TableRow></TableHeader><TableBody>{stats.records.map(row=><TableRow key={row.id}><TableCell>{new Date(row.created).toLocaleString("ko-KR")}<p>{row.snapshot.query.slice(0,40)}</p></TableCell><TableCell>{row.snapshot.config.size} / {row.snapshot.config.overlap} / {row.snapshot.config.topK} / {row.snapshot.config.budget}<p>재정렬 {row.snapshot.config.rerank?"ON":"OFF"} · T {row.snapshot.settings.temperature}</p></TableCell><TableCell>약 {row.estimate.inputTokens} / {row.estimate.outputLimit}</TableCell><TableCell>{usd(row.estimate.totalUsd)}</TableCell><TableCell>{row.status==="complete"?`${row.input_tokens??"?"} / ${row.output_tokens??"?"} · ${row.cost===null?"미확인":usd(row.cost)}`:row.status?"처리 중 / 비용 미확인":"추론 안 함 · $0"}</TableCell><TableCell><Button size="sm" variant="outline" onClick={()=>load(row)}>B로 복원</Button><details><summary>저장 내용</summary><pre className="data-code">{row.snapshot.system+"\n\n"+row.snapshot.document}</pre>{row.output&&<p className="generated-text">{row.output.text}</p>}<small>{row.estimate.price}</small></details></TableCell></TableRow>)}</TableBody></Table></div><p className="muted">최근 50개 표시 · 합계는 전체 기록 기준입니다. 저장된 답변을 재사용하면 실제 토큰 합계가 증가하지 않습니다.</p></>:<p className="empty-copy">통계를 불러오는 중이거나 저장소 연결을 기다리고 있습니다. 예상 비용은 계속 계산됩니다.</p>}
 </section>;
}
