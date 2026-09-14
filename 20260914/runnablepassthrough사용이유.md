Read d:\hanwha_0902\20260914\langsmith_runnable_test.ipynb
RunnablePassthrough란?
LangChain의 LCEL(| 파이프라인)에서 사용하는 항등(identity) Runnable입니다. 입력을 받아 아무 변형 없이 그대로 출력으로 내보내는 역할만 합니다.


RunnablePassthrough().invoke({"num": 11})
# {'num': 11}  ← 입력 그대로 반환
노트북의 langsmith_runnable_test.ipynb 셀 ef8a1323에서 확인한 것과 정확히 이 동작입니다.

구동 원리
Runnable 인터페이스: LCEL의 모든 컴포넌트(PromptTemplate, ChatOpenAI, StrOutputParser 등)는 invoke/batch/stream 등을 구현한 Runnable입니다. RunnablePassthrough는 이 인터페이스를 구현하되 로직이 return input 뿐입니다.

dict → RunnableParallel 자동 변환: LCEL에서 {"key": runnable_or_callable} 형태의 dict를 파이프(|)에 넣으면 내부적으로 coerce_to_runnable이 이를 RunnableParallel로 변환합니다. RunnableParallel은 같은 입력을 각 value에 병렬로 전달하고, 결과를 key별로 모아 하나의 dict로 합칩니다.


runnable_chain = {"num": RunnablePassthrough()} | prompt | ChatOpenAI()
runnable_chain.invoke(13)
여기서 13이라는 입력이 RunnableParallel({"num": RunnablePassthrough()})에 들어가고, RunnablePassthrough()가 13을 그대로 통과시켜 {"num": 13}을 만든 뒤 prompt로 전달됩니다. 이게 셀 4cba4293이 동작하는 원리입니다.

RunnablePassthrough.assign(**kwargs): 내부적으로 RunnableAssign이라는 클래스로, 동작은 다음과 같습니다.

입력(반드시 dict/mapping)을 그대로 보존하면서
kwargs로 준 함수/Runnable들을 같은 입력에 대해 실행하고
그 결과를 원본 dict에 새 key로 **병합(merge)**해서 반환합니다.

RunnablePassthrough.assign(new_num=lambda x: x["num"] * 7).invoke({"num": 3})
# {'num': 3, 'new_num': 21}
셀 b9ee2757에서 에러가 난 이유가 바로 이 원리 때문입니다 — assign은 "원본 dict + 새 필드"를 만드는 연산이라 입력이 dict(mapping)여야만 동작합니다. x["num"]처럼 key로 접근하는 lambda를 실행해야 하고, 병합 대상도 dict여야 하기 때문입니다. 만약 int 같은 non-dict를 넣으면 (에러 트레이스백에 나온 것처럼) coerce_to_runnable/RunnableParallel 쪽에서 "Expected a Runnable, callable or dict... got int" 에러가 납니다.

왜 사용하는가
가장 흔한 사용 이유는 원본 입력을 잃지 않고 다음 단계로 전달하기 위해서입니다. 대표적으로 RAG 체인:


chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
)
retriever는 질문(question)을 받아 문서를 검색하지만, 정작 프롬프트 템플릿에는 원본 질문(question)도 그대로 필요합니다. retriever만 쓰면 원본 질문이 사라지므로, RunnablePassthrough()로 원본 입력을 "복사해서 그대로" 옆 key에 흘려보내는 것입니다.

정리하면:

RunnablePassthrough(): 입력을 변형 없이 그대로 다음 단계로 넘길 때 (병렬 체인 중 한쪽 값을 원본 그대로 유지)
RunnablePassthrough.assign(...): 기존 입력 dict를 유지한 채, 계산된 새 필드를 추가해서 넘길 때 (파이프라인 중간에 값을 누적/보강)