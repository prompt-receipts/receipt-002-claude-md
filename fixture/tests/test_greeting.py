from app.features.greeting import greet


def test_greet():
    assert greet("Ann") == "Hello, Ann!"
