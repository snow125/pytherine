__author__ = 'root'

class A:
    a = 'a'
    def set(self):
        print self.a
class B(A,object):
    a = 'b'
    def set(self):
        func = A.set(self)

def test_func():
    pass

if __name__ == '__main__':
    # bb = B()
    # bb.set()
    print test_func.__name__