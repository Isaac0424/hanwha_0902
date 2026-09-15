"use client";
import {createContext,useContext,useState,useMemo,useEffect,useCallback,useRef,type ReactNode} from "react";
import {DRAFT_KEY,parseDraft,serializeDraft} from "@/lib/workspace-draft";
import {usePathname} from "next/navigation";
import {Workflow,GitCompareArrows,History,KeyRound,BookOpen} from "lucide-react";
import {calculate,DEFAULT_CONFIG,DEFAULT_DOCUMENT,DEFAULT_QUERY,DEFAULT_SYSTEM,type Result} from "@/lib/rag-engine";
import {estimateCost,stableInput,type ExperimentInput} from "@/lib/cost";
import type {Generation} from "@/lib/generation";
export type RecordRow={id:string;created:number;snapshot:ExperimentInput;estimate:ReturnType<typeof estimateCost>;status:string|null;output:Generation|null;input_tokens:number|null;output_tokens:number|null;cost:number|null};
export type Stats={records:RecordRow[];configured:boolean;totals:{experiments:number;calls:number;completed:number;unknown:number;inputTokens:number;outputTokens:number;cost:number}};
export const initial:ExperimentInput={query:DEFAULT_QUERY,document:DEFAULT_DOCUMENT,system:DEFAULT_SYSTEM,config:DEFAULT_CONFIG,settings:{temperature:0,maxTokens:512}};
type LabContext={input:ExperimentInput;baseline:ExperimentInput;result:Result;a:Result;update:(p:Partial<ExperimentInput>)=>void;pin:()=>void;setBaseline:(i:ExperimentInput)=>void;stats:Stats|null;refresh:()=>Promise<void>;saveMessage:string;auth:boolean|null;error:string};
const Context=createContext<LabContext|null>(null);
export function useLab(){const v=useContext(Context);if(!v)throw Error("Workspace unavailable");return v;}
const nav=[{href:"/",label:"파이프라인",icon:Workflow},{href:"/compare",label:"A/B 비교·생성",icon:GitCompareArrows},{href:"/history",label:"실험 기록",icon:History},{href:"/connection",label:"모델 연결",icon:KeyRound},{href:"/guide",label:"학습 가이드",icon:BookOpen}];
export function Workspace({children}:{children:ReactNode}){
 const path=usePathname(),[input,setInput]=useState(initial),[baseline,setBaselineState]=useState(initial),[stats,setStats]=useState<Stats|null>(null),[auth,setAuth]=useState<boolean|null>(null),[error,setError]=useState(""),[saveMessage,setSave]=useState("로컬 실험 준비됨");
 const touched=useRef(false),hydrated=useRef(false),[ready,setReady]=useState(false);
 const inputRef=useRef(initial),baselineRef=useRef(initial);
 const persist=useCallback(()=>{try{sessionStorage.setItem(DRAFT_KEY,serializeDraft({input:inputRef.current,baseline:baselineRef.current}));}catch{/* Saving to the server remains available when tab storage is disabled. */}},[]);
 const update=useCallback((p:Partial<ExperimentInput>)=>{touched.current=true;const next={...inputRef.current,...p};inputRef.current=next;setInput(next);persist();},[persist]);
 const setBaseline=useCallback((next:ExperimentInput)=>{touched.current=true;baselineRef.current=next;setBaselineState(next);persist();},[persist]);
 useEffect(()=>{try{const draft=parseDraft(sessionStorage.getItem(DRAFT_KEY));if(draft){touched.current=true;inputRef.current=draft.input;baselineRef.current=draft.baseline;setInput(draft.input);setBaselineState(draft.baseline);}}catch{}},[]);
 const refresh=useCallback(async()=>{try{const response=await fetch("/api/experiments",{cache:"no-store"});if(response.status===401){setAuth(false);setSave("localhost 주소로 접속하세요");return;}const data=await response.json() as Stats&{error?:string};if(!response.ok)throw Error(data.error||"저장소 연결 오류");setAuth(true);setStats(data);setError("");if(!hydrated.current){hydrated.current=true;if(!touched.current&&data.records[0]){inputRef.current=data.records[0].snapshot;setInput(data.records[0].snapshot);}}setReady(true);}catch{setError("기록을 불러오지 못했습니다. 연결을 확인하고 다시 시도하세요.");}},[]);
 useEffect(()=>{void refresh();},[refresh]);
 const signature=stableInput(input);
 useEffect(()=>{if(!ready||auth!==true)return;let active=true;setSave("변경 중…");const timer=setTimeout(async()=>{try{const r=await fetch("/api/experiments",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(input)});if(r.status===401){setAuth(false);return;}if(!r.ok)throw Error();if(active){setSave("저장됨");void refresh();}}catch{if(active)setSave("저장 실패 · 기록 페이지에서 재시도하세요");}},800);return()=>{active=false;clearTimeout(timer)};},[signature,ready,auth,refresh]);
 const result=useMemo(()=>calculate(input.query,input.document,input.system,input.config),[input.query,input.document,input.system,input.config]);
 const a=useMemo(()=>calculate(baseline.query,baseline.document,baseline.system,baseline.config),[baseline]);
 return <Context.Provider value={{input,baseline,result,a,update,pin:()=>setBaseline(input),setBaseline,stats,refresh,saveMessage,auth,error}}><div className="studio-shell"><aside className="studio-nav"><a href="/" className="studio-brand"><img src="/logo-cat.png" alt="" className="studio-logo"/><span>RAG <b>Explorer</b><small>INTERACTIVE WORKSPACE</small></span></a><p className="nav-label">WORKSPACE</p><nav>{nav.map(n=><a key={n.href} href={n.href} aria-current={path===n.href?"page":undefined}><n.icon size={18}/>{n.label}{n.href==="/connection"&&!stats?.configured&&<i/>}</a>)}</nav><div className="nav-note"><span className="live-dot"/>LOCAL FIRST<p>설정 변경은 무료<br/>모델은 직접 실행할 때만 호출</p></div></aside><div className="studio-body"><header className="studio-top"><span>{nav.find(n=>n.href===path)?.label||"RAG Explorer"}</span><div><small role="status">{saveMessage}</small><a href="/connection" className={stats?.configured?"connected-pill":"connect-pill"}>{stats?.configured?"환경변수 연결됨":"모델 연결하기"}</a></div></header>{auth===false&&<div className="auth-banner"><span>로컬 서버 주소로 접속해야 기록을 저장할 수 있습니다.</span><a href="http://127.0.0.1:3000">로컬 서버 열기</a></div>}<main className="studio-main">{children}</main></div></div></Context.Provider>;
}
