
class Result:
    def __init__(self,user_name,competency,language):
        self.user_name = user_name
        self.competency = competency
        self.language = language
    
    def __repr__(self):
        return str({
                "user_name" : self.user_name,
                "competency" : self.competency,
                "language" : self.language
                })
            
        