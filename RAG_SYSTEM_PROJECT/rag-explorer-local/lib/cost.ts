import type {Result,Config} from "./rag-engine";
import type {GenerationSettings} from "./generation";
export const PRICE={input:.10,output:.40,version:"참고 추정 단가 / Gemini 3.5 Flash-Lite 최신 가격표 확인 필요"};
export type ExperimentInput={query:string;document:string;system:string;config:Config;settings:GenerationSettings};
export function estimateCost(r:Result,s:GenerationSettings){
 const inputTokens=Math.ceil(r.prompt.length/3)+16;
 return {inputTokens,promptChars:r.prompt.length,contextChars:r.context.length,selectedChunks:r.selected.length,outputLimit:s.maxTokens,inputUsd:inputTokens*PRICE.input/1e6,outputBudgetUsd:s.maxTokens*PRICE.output/1e6,totalUsd:(inputTokens*PRICE.input+s.maxTokens*PRICE.output)/1e6,price:PRICE.version,method:"offline chars/3 + 16; output at configured limit",changeCostUsd:0};
}
export function experimentInput(r:Result,s:GenerationSettings):ExperimentInput{return {query:r.query,document:r.document,system:r.system,config:r.config,settings:s};}
export function stableInput(i:ExperimentInput){return JSON.stringify([i.query,i.document,i.system,i.config.size,i.config.overlap,i.config.topK,i.config.rerank,i.config.budget,i.settings.temperature,i.settings.maxTokens]);}
