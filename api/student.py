import uuid


class student:
    def __init__(self,name,surname,age,level):
        self.id = uuid.uuid4()
        self.name=name
        self.age=age
        self.level=level
        self.surname=surname

    def get_id(self):
        return self.id

    def get_student(self):
        return (f"name: {self.name}\nsurname: {self.surname}\nage: {self.age}\nlevel: {self.level}")

    def get_params(self):
        return (self.id,self.name,self.surname,self.age,self.level)
