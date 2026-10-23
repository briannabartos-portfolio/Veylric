# Veylric

A JARVIS-inspired personal AI assistant built with Python and Ollama on macOS.

Veylric is a learning and portfolio project: I am building it incrementally while learning Python, explaining the code, testing small changes, and documenting limitations. Development includes AI-assisted guidance and code review.

**Status:** Beta 0.2 milestone completed; Beta 0.3 is in development. This is an experimental terminal application, not a production assistant.

## Current abilities

- Stream conversational replies from the locally running `ministral-3:8b` model.
- Retain the latest five completed chat exchanges in memory; `clear conversation` resets that context.
- Record what tools actually did (sent, verified, unconfirmed, cancelled, or failed) as action records in the in-memory conversation, so Veylric can answer questions such as "did that work?" honestly and say when it has no record of an action. No conversation is saved to disk by the application.
- Open Spotify, Chrome, and Messages, and request Chrome to quit if it is running.
- Confirm that Spotify actually started by checking macOS for up to five seconds, and report whether it was already open, verified, or unconfirmed.
- Answer time and date questions from the Mac's clock; conversational replies also receive the current date and time.
- Classify natural requests to open, search, and control Spotify using a restricted set of labels, including song requests that do not name Spotify. The classifier is only consulted when a message contains a music or search word such as play, song, music, search, or pause. In the current Beta 0.3 working code, a clear opening request runs without a second confirmation.
- Ask for clarification on ambiguous Spotify requests and use one-turn context for the tested follow-ups `open it` and `launch it`.
- Search Spotify from typed commands or natural requests such as "could you find Fleetwood Mac on Spotify?". The model extracts the search words; Python keeps only words the user actually said. Searches run directly and are verified by checking that Spotify is running; if the model tried to add words, Veylric shows a preview and asks for `SEARCH` approval first. Search does not request playback.
- Report what Spotify is playing, and pause, resume, skip, or go back, using exact phrases such as `pause music` or natural requests such as "could you pause my music?", classified into allowlisted labels. Each control is verified by reading Spotify's state afterwards, and Veylric never launches Spotify just to check it. Playing a song by name is not supported; see the [playback investigation](docs/playback-investigation.md).
- Use session context for searches: `search it again` repeats the last search, `search for Adele` works as an answer to Spotify clarification, and requests such as "search for them on Spotify" are resolved from the in-memory conversation. Words from the user's earlier messages run directly with a note; words that only appear in Veylric's own replies require `SEARCH` approval. `clear conversation` also forgets the last search.
- Preview organization of `.jpg` and `.txt` files in a dedicated practice folder; unknown types stay unchanged.
- Attempt approved practice-file moves with source checks, destination checks, macOS no-overwrite protection, and outcome counts.

## How it works

```text
Typed request
    ├── Defined command → Python tool
    ├── Time/date question → Python reads the clock
    ├── Mentions Spotify → model classifier → validated label
    │                  ├── Spotify tool or clarification
    │                  └── conversational response
    └── Anything else → conversational response
```

The model suggests labels; Python selects from implemented behaviors. Model output is not executed as shell commands. File moves require `APPROVE`; app opening and Spotify searches run immediately, with a `SEARCH` check only when extracted search words looked suspicious. These controls have been tested in disposable folders, but are not a security sandbox.

## Setup

The project has been exercised with Python 3.14, Ollama's Python package 0.6.3, and a MacBook Air. App-launching and protected file-moving code are macOS-specific.

1. Install Python and [Ollama](https://ollama.com/), and start Ollama.
2. In the repository folder, create a virtual environment and install the Python dependency:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Download the model if needed:

   ```bash
   ollama pull ministral-3:8b
   ```

   Model downloads consume storage; runtime memory and speed depend on the machine and conversation length.

4. Create the disposable test folders (their contents are intentionally excluded from Git):

   ```bash
   mkdir -p veylric_beta/practice_files veylric_beta/move_test
   ```

5. Run the working assistant:

   ```bash
   python veylric_beta/main.py
   ```

Spotify and Chrome commands require those applications to be installed. macOS may request automation permission for quitting Chrome. Terminal transcripts remain visible after conversation history is cleared.

## Try it

```text
Hello Veylric.
What time is it?
What's the date?
What's playing?
next song
Could you open Spotify, please?
search spotify for Fleetwood Mac
search it again
Who sang Dreams?
Search for them on Spotify
clear conversation
shutdown
```

For file experiments, create disposable files in `veylric_beta/practice_files`. `organize my files` (or `organise my files`) previews the plan; `move practice files` can perform real moves within that folder after approval. Suggested destinations are its `Pictures` and `Documents` subfolders, not the Mac's personal folders. Keep real documents out of these test folders.

`test file move` is a development exercise for `veylric_beta/move_test/move_me.txt`. It requires approval and attempts to move that file into the test folder's `Documents` subfolder.

## Project layout

| File | Responsibility |
| --- | --- |
| `veylric_beta/main.py` | Main loop, chat, app tools, file preview and moves |
| `veylric_beta/intent_test.py` | Reusable classifier and standalone test |
| `veylric_beta/spotify_search_test.py` | Reusable Spotify search and standalone test |
| `veylric_beta/chat_test.py` | Small streaming experiment |
| `veylric_beta/README.md` | Milestone and testing notes |

## Validation so far

For a section-by-section explanation of the current code, learning evidence, and topics to revisit, see the [code and learning walkthrough](docs/code-walkthrough.md). It is an AI-assisted study guide; personal reflection prompts are left for the learner to complete.

Manual terminal tests covered streaming, session recall and clearing, case-insensitive commands, clarification and cancellation, Spotify searches, and Ollama connection/missing-model errors. Beta 0.3 checks covered opening Spotify when closed and when already open, and time/date phrase detection, including questions such as "what time does the shop close" that should go to conversation instead. File tests covered approved moves, empty/missing folders, missing source files, and occupied destinations. Isolated temporary-file tests exercised the macOS no-overwrite helper; pretend-move tests checked success/skip/failure counters.

These are development checks, not a comprehensive automated test suite. A model passing an example does not guarantee correct classification on every request.

## Known limitations

- Natural tool interpretation currently supports Spotify opening, search, and playback controls, not arbitrary tools. The model sometimes wraps labels in Markdown, which Python strips before the exact allowlist check. Negation and ambiguity have been tested with examples but can still be misclassified.
- Search supports defined command formats; the installed Spotify client displays plus signs between words in URI searches. Two queries produced relevant results, but special-character handling needs broader testing.
- Spotify opening is verified by checking that the app is running; Chrome and Messages report only that macOS accepted the request. Veylric does not verify an app's screen or playback.
- Time and date questions are recognized from a fixed list of phrases; other wordings go to the model, which receives the current time but can still answer incorrectly.
- Contextual search depends on the model resolving words like "them"; it can return nothing or mix in extra words from Veylric's replies, which then triggers the `SEARCH` check. Reference words are only recognized directly after search, find, play, for, or up.
- Conversation can invent facts, miss style instructions, or reuse stale context. Action records tell the model what tools did, but the model can still phrase them too cautiously or offer abilities it does not have, such as checking search results.
- History is limited by message count, not token length. Some filesystem errors and interrupted input/streams are not handled yet.
- Practice paths are fixed in code but are not hardened confinement boundaries; symbolic links and file changes between checks need further review before any real-data use.
- No deletion, email/calendar access, persistent personal memory, voice, or camera/screen capture is implemented.

## Roadmap

- **Beta 0.3:** smoother Spotify conversation (clear requests, clarification, and verified opening done), actual date/time (done), natural and contextual search (done), and a playback investigation with basic verified controls (done).
- **Beta 0.4:** document workflows, explicit folder access, stronger file safeguards, and recovery controls.
- **Beta 0.5:** on-demand visual assistance, with separate camera/screen choices and explicit capture controls.
- **Later:** push-to-talk voice, a JARVIS-inspired interface, and user-controlled persistent memory.

This is an independent educational project inspired by fictional assistants, with no affiliation to Marvel, Spotify, or Ollama.
