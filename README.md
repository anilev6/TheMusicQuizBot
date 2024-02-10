# VictorynaBot 🎧 - The Music Quiz Bot

*Welcome to [VictorynaBot](https://t.me/AcademyVictorynaBot), another my pet project!*

VictorynaBot is a Telegram bot designed for teachers and students engaged in music-related subjects. It transforms homework into an interactive music-listening quiz.

❗️This is currently a beta version for testing among friends, and the teachers are manually added.
If the bot proves to be useful, further development will be pursued.

Here's how it works:

- Teachers upload mp3 audio files (up to 4 MB), create a quiz (called a Victoryna), provide a name and description, and then launch it.

- Students can then initiate the Victoryna, receive a voice message containing the music piece, and respond with their answers. Once all tracks have been answered, the quiz ends and students receive their results instantly via a message.

- Upon completion of the Victoryna, the results are compiled and sent to the teacher in an Excel file.

## Project Features

- To deter cheating via file size or length, each audio is appended with a random-length silence before being sent to a student. This ensures that the audio tracks always appear different for each student.

- Students receive audios as secure voice messages, preventing unauthorized uploading or forwarding of the audio.

- Teachers have full control over their Victorynas and audios, with the ability to perform all CRUD operations.

### Commands

- `/start` the bot
- `/cancel` if needed
- `/menu` for the teacher
- to upload audio, a teacher simply drops it to the chat

### TODO

- [ ] Address the issue where not all mp3 files can be encoded into a format readable by iOS; for other systems, it's always readable.

- [ ] Explore the possibility of scaling this bot for many teachers.

- [ ] Consider [switching to webhooks](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks) for improved performance.

- [ ] Develop a comprehensive data privacy notice.

*Stay tuned for more updates, I wish I had more time...*
