def test_chatbot():
    chatbot = Chatbot()
    response = chatbot.get_response("你好")
    assert response == "你好！有什么我可以帮助你的吗？"

if __name__ == '__main__':
    test_chatbot()