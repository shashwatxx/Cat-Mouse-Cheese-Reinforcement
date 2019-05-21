class Student:
    pri = 'Vishruti'
    def __init__(self, name):
        self.name = name
    def printName(self):
        print("Name is %s" %self.name)
    @staticmethod
    def printPri():
        print('Principal is %s' % Student.pri)

s1 = Student('Ajay')
s2 = Student('Vikash')
print(Student.pri)
Student.pri = "Niharika";
print(Student.pri)
s1.printName()
s2.printName()
Student.printPri()
