child1 = {
    "name":"Emilly",
    "year":2004
}

child2 = {
    "name":"Tobias",
    "year":2007
}

child3 = {
    "name":"Linus",
    "year":2011
}

child4 = {
    "name":"Isaac",
    "year":1995
}
myfamily = {
    "child1":child1,
    "child2":child2,
    "child3":child3,
    "child4":child4
}
def test_dictionary():
    print(myfamily)
    for k,v in myfamily.items():
        print(f"{k} : {v}")
        
if __name__ == "__main__":
    test_dictionary()
    a=5
    b=3
    print("true") if a<b else print("false")
    
    data=range(10)
    b = [x for x in data]
    print(b)
    print(data)