from pathlib import Path

paths = [
    str(Path(__file__).parent / "Quidditch_Match.ogg"),
    str(Path(__file__).parent / "Baby_Harry.ogg"),
    str(Path(__file__).parent / "Morning_Passages.ogg"),
]

audios = [
    {
        "file_path": paths[0],
        "description": "John Williams, Harry Potter - The Quidditch Match",
    },
    {
        "file_path": paths[1],
        "description": "John Williams, The Arrival of Baby Harry",
    },
    {
        "file_path": paths[2],
        "description": "The Hours - Philip Glass - Morning Passages",
    },
]

victorynas = [
    {
        "audios": [audios[0], audios[2]],
        "title": "Тестова вікторина",
        "description": "Вступна вікторина для 1 рік, 4та група\nФіліп Глас чи Джон Вільямс?",
    },
    {
        "audios": [audios[0], audios[1]],
        "title": "Magical Melodies: The Harry Potter Edition",
        "description": "Test your knowledge of the iconic melodies that accompanied Harry, Hermione, and Ron on their adventures.",
    },
]
