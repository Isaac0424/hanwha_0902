#import
from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError

#Class 
class User(BaseModel):
    id : int
    name : str = 'John Doe'
    signup_ts : datetime | None
    tastes : dict[str, PositiveInt]
    
#Data
external_data = {
    'id' : 123,
    'signup_ts' : '2019-06-01 12:22',
    'tastes': {
        'wine' : 9,
        b'cheese' : 7,
        'cabbage' : '1',
    },
}

# Wrong Data
external_data_2 = {
    'id' : 'not an int',
    'tastes' : {}
}

if __name__ == "__main__":
    #  '**'을 붙이는 이유는 ditionay unpacking이다.
    #  class 초기화시에 딕셔너리 값을 통째로 넣어주는 것보다 언패킹하여서 Class와 형태를 맞춰줌. 
    user = User(**external_data)
    print(user.id)
    #> 123
    
    print(user.model_dump())
    """
    {
        'id' : 123,
        'name' : 'John Doe',
        'signup_ts' : datetime.datetime(2019, 6, 1, 12, 22),
        'tastes' : {'wine' : 9, 'cheese' : 7, 'cabbage' : 1}, 
    
    }
    """
    print(type(user.tastes['cabbage']))
    #type 을 변경해줌.
   
    try:
       User(**external_data_2)
    except ValidationError as e:
        print(e.errors())
    except:
        print("Validation Error가 아닌 경우 다음 exeption 탐색")
    else:
        print("exception들이 실행되지 않으면 즉 try구문이 정상실행되면 해당 구간 실행")
    finally:
        print("항상 마지막에 실행 예를 들어 파일 시스템 실행시 마지막에 f.close()로 사용")
        
    """
    [
        {
            'type': 'int_parsing', 
            'loc': ('id',), 
            'msg': 'Input should be a valid integer, unable to parse string as an integer', 
            'input': 'not an int', 
            'url': 'https://errors.pydantic.dev/2.13/v/int_parsing'
        }, 
        {
            'type': 'missing', 
            'loc': ('signup_ts',), 
            'msg': 'Field required', 
            'input': {'id': 'not an int', 'tastes': {}}, 
            'url': 'https://errors.pydantic.dev/2.13/v/missing'
        }
    ]
    """