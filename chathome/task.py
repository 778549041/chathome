
class Task:
    def __init__(self, account, password, wordContent, chatRoomId, chatRoomUrl, carSeriesName, memberName=None):
        self.account = account
        self.password = password
        self.wordContent = wordContent
        self.chatRoomId = chatRoomId
        self.chatRoomUrl = chatRoomUrl
        self.carSeriesName = carSeriesName
        self.memberName = memberName
        self.taskType = 1   # 1:回复 2:定时
        self.id = 0
        self.doTime = None
        self.taskTime = None
