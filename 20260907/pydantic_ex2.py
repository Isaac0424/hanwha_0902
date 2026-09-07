from typing import Annotated, Literal
from annotated_types import Gt
from pydantic import BaseModel
from datetime import datetime

# Annotated는 추가 값을 검증하기 위한 기능
# Gt(x) 는 Grater than 즉 ()안의 매개 변수 x 보다 값이 커야한다는 의미이다.
#Literal의 경우 [ ]안에 있는 'red' 혹은 'green' 만 가능하다.

class Fruit(BaseModel):
    name: str
    color: Literal['red', 'green']
    weight: Annotated[float, Gt(0)]
    bazam: dict[str, list[tuple[int, bool, float]]]
def testTypeHint():
    print(
        Fruit(
            name= 'Apple', 
            color= 'red',
            weight= 4.2,
            bazam= {'foobar': [(1, True, 0.1)]},
        )    
    )
    
class Meeting(BaseModel):
    when: datetime
    where: bytes
    why: str = 'No idea'
    
    
#serialization 직렬화는 pydantic 객체를 dictionary 또는 json화 하는 것
#model_dump를 통해 직렬화되고 안에 매개변수 옵션 설정이 가능하다.

def test_serialization_3_ways():
    m = Meeting(when= '2020-01-01T12:00', where= 'home')
    
    print(m.model_dump(exclude_unset=True))
    #{'when': datetime.datetime(2020, 1, 1, 12, 0), 'where': b'home'}
    print(m.model_dump(exclude= {'where'}, mode= 'json'))
    print(type(m.model_dump(exclude= {'where'}, mode= 'json')))
    #{'when': '2020-01-01T12:00:00', 'why': 'No idea'}
    #반환 타입이 Dictionary
    print(m.model_dump_json(exclude_defaults=True))
    print(type(m.model_dump_json(exclude_defaults=True)))
    #{"when":"2020-01-01T12:00:00","where":"home"
    #반환 타입이 String

if __name__ == "__main__":
    # testTypeHint()
    test_serialization_3_ways()
    