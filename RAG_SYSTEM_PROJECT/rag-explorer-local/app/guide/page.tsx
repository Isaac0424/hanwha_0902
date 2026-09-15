"use client";
import {Guide} from "@/components/lab-details";
export default function Page(){return <><div className="page-title"><div><p>LEARN BY EXPLORING</p><h1>학습 가이드</h1><span>원리 설명은 이곳에서, 실험은 파이프라인에서.</span></div></div><Guide onStart={()=>window.location.assign("/")}/></>}
