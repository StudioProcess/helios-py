import math as _math

# Column major matrix
class matrix(list):
    # TODO: suppport the folowing:
    # matrix(1,2): [[1,2]]
    # matrix([1,2]): [[1,2]]
    # matrix([1,2], [3,4]): [[1,2], [3,4]]
    # matrix([1], [2]): [[1], [2]]
    # matrix([[1,2], [3,4]]): [[1,2], [3,4]]
    def __init__(self, cols):
        # TODO: check that cols is 2d vector or 2d matrix
        # cols is just an array (not containing column sub-arrays): treat it as single column (vector)
        if type(cols[0]) is not list:
            cols = [cols]

        super().__init__(cols)
    
    # number of columns
    def ncols(self): 
        return len(self)
    
    # number of rows
    def nrows(self):
        return len(self[0])
    
    def col(self, n):
        return self[n]
    
    def row(self, n):
        return [ col[n] for col in self ]
    
    def cols(self):
        return list(self)
    
    def rows(self):
        return [ self.row(i) for i in range(self.nrows()) ]
    
    # self * b
    def __mul__(self, b):
        # TODO number of cols in self == number of rows in b
        if type(b) is list: b = matrix(b) # support lists for b
        cols = []
        for bcol in b.cols():
            col = []
            for arow in self.rows():
                col.append( sum( map( lambda x: x[0]*x[1], zip(arow, bcol) ) ) )
            cols.append(col)
        return matrix(cols)
    
    # a * self
    def __rmul__(self, a):
        if type(a) is list: a = matrix(a)
        return a.__mul__(self)
    
    # self @ b
    def __matmul__(self, b):
        return self.__mul__(b)
    
    # a @ self
    def __rmatmul__(self, a):
        return self.__rmul__(a)


def identity():
    return matrix([ [1, 0, 0], [0, 1, 0], [0, 0, 1] ])

def translate(tx, ty):
    return matrix([ [1, 0, 0], [0, 1, 0], [tx, ty, 1] ])

def scale(sx, sy, ox = 0, oy = 0):
    if sy is None: sy = sx
    return (
        translate(ox, oy) * 
        matrix([ [sx, 0, 0], [0, sy, 0], [0, 0, 1] ]) *
        translate(-ox, -oy)
    )

def flipx(x = 0):
    return (
        translate(x, 0) * 
        scale(-1, 1) * 
        translate(-x, 0)
    )

def flipy(y = 0):
    return (
        translate(0, y) * 
        scale(1, -1) *
        translate(0, -y)
    )

def swapxy():
    return matrix([ [0, 1, 0], [1, 0, 0], [0, 0, 1] ])

# clockwise rotation (assuming x points right, y points up)
def rotate(deg, ox = 0, oy = 0, ccw = False):
    rad = _math.radians(deg)
    cos = _math.cos(rad)
    sin = _math.sin(rad)
    return (
        translate(ox, oy) *
        matrix([ [cos, sin if ccw else -sin, 0], [-sin if ccw else sin, cos, 0], [0, 0, 1] ]) *
        translate(-ox, -oy)
    )

if __name__ == '__main__':
    a = matrix([ [1, 2], [3, 4] ])
    b = matrix([ [1, 3], [2, 4] ])
    print(a)
    print(a.ncols())
    print(a.nrows())
    print(a.cols())
    print(a.rows())
    print(a * b)
    print(a @ b)

    print(a * matrix([1, 2]))
    print(a * [1, 2])
    
    print( [ [1, 2], [3, 4] ] * matrix([1,2]) )
