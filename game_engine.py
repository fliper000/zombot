class Game():
    def start(self):
        # load items dictionary

        # send TIME request (http://java.shadowlands.ru/zombievk/go)
        # handle redirect (save new url: http://95.163.80.20/zombievk)
        # parse auth key and time id
        self.getTime()

        # get vk user info

        # send START

        # parse game state

        # send getMissions

        # handle getMissions response

        # in a loop, every 30 seconds
        # send EVT request
        # handle EVT response
        
    def getTime(self):
        return {}
