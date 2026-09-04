import time
from functools import wraps

DEBUG = True

def runtimeWrapper(func):
    '''Wrapper to measure the runtime of a function'''
    @wraps(func)
    def debugWrapper(*args, **kwargs):
        start_time = time.time()
        print("-------------------------------")
        func(*args, **kwargs)
        print("-------------------------------")
        end_time = time.time()
        print(f"Function name: {func.__name__}")
        print(f"Execution time: {round(end_time - start_time, 10)} seconds")
        print("-------------------------------")
    @wraps(func)
    def releaseWrapper(*args, **kwargs):
        func(*args, **kwargs)

    return debugWrapper if DEBUG else releaseWrapper

@runtimeWrapper
def printSchedule():
    '''Prints the schedule of subjects and their corresponding times'''
    topic = "AI 서비스 백엔드 프로그래밍 실무"
    line = "================================"
    connection_world_subject2time = ", 시간: "
    subject_time = {"파이썬 기본 문법": 8, "클래스" : 8, "데코레이터":8, "예외 처리":8, "로깅":8}

    result = f"{topic}\n{line}\n"
    # max_length_subject_name = max(len(s) for s in subject_time.keys())
    for subject, time in subject_time.items():
        # result += f"{subject.ljust(max_length_subject_name,' ')}{connection_world_subject2time}{time}\n"
        result += f"{subject}{connection_world_subject2time}{time}\n"
    print(result.rstrip("\n"))

def run():
    printSchedule()


if __name__ == ("__main__"):
    run()
    