# Veylric

A JARVIS-inspired personal AI assistant built with Python and Ollama on macOS.

Veylric is a learning and portfolio project: I am building it incrementally while learning Python, explaining the code, testing small changes, and documenting limitations. Development includes AI-assisted guidance and code review.

**Status:** Beta 0.2 milestone completed; Beta 0.3 is in development. This is an experimental terminal application, not a production assistant.

## Current abilities

- Stream conversational replies from the locally running `ministral-3:8b` model.
- Retain the latest five completed chat exchanges in memory; `clear conversation` resets that context. No conversation is saved to disk by the application.
- Open Spotify, Chrome, and Messages, and request Chrome to quit.
- Classify natural requests to open Spotify using a restricted set of labels. In the current Beta 0.3 working code, a clear opening request runs without a second confirmation.
- Ask for clarification on ambiguous Spotify requests and use one-turn context for the tested follow-ups `open it` and `launch it`.
- Open Spotify search results after a preview and explicit `SEARCH` confirmation. Search does not request playback.
- Preview organization of `.jpg` and `.txt` files in a dedicated practice folder; unknown types stay unchanged.
- Attempt approved practice-file moves with source checks, destination checks, macOS no-overwrite protection, and outcome counts.

## How it works

```text
Typed request
    ├── Defined command → Python tool
    └── Otherwise → model classifier → validated label
                       ├── Spotify tool or clarification
                       └── conversational response
```

The model suggests labels; Python selects from implemented behaviors. Model output is not executed as shell commands. File moves require `APPROVE`; exact app-opening commands run immediately. These controls have been tested in disposable folders, but are not a security sandbox.

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
Could you open Spotify, please?
search spotify for Fleetwood Mac
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

Manual terminal tests covered streaming, session recall and clearing, case-insensitive commands, clarification and cancellation, Spotify searches, and Ollama connection/missing-model errors. File tests covered approved moves, empty/missing folders, missing source files, and occupied destinations. Isolated temporary-file tests exercised the macOS no-overwrite helper; pretend-move tests checked success/skip/failure counters.

These are development checks, not a comprehensive automated test suite. A model passing an example does not guarantee correct classification on every request.

## Known limitations

- Natural tool interpretation currently supports Spotify opening, not arbitrary tools. Negation and ambiguity have been tested with examples but can still be misclassified.
- Search supports defined command formats; the installed Spotify client displays plus signs between words in URI searches. Two queries produced relevant results, but special-character handling needs broader testing.
- App-opening success means macOS accepted the request; Veylric does not verify the app's screen or playback.
- Conversation can invent facts, miss style instructions, or reuse stale context. Tool results are not yet supplied to chat as a structured action record.
- History is limited by message count, not token length. Some filesystem errors and interrupted input/streams are not handled yet.
- Practice paths are fixed in code but are not hardened confinement boundaries; symbolic links and file changes between checks need further review before any real-data use.
- No deletion, email/calendar access, persistent personal memory, voice, or camera/screen capture is implemented.

## Roadmap

- **Beta 0.3:** smoother Spotify conversation, contextual search, actual date/time, and a separate playback feasibility investigation.
- **Beta 0.4:** document workflows, explicit folder access, stronger file safeguards, and recovery controls.
- **Beta 0.5:** on-demand visual assistance, with separate camera/screen choices and explicit capture controls.
- **Later:** push-to-talk voice, a JARVIS-inspired interface, and user-controlled persistent memory.

This is an independent educational project inspired by fictional assistants, with no affiliation to Marvel, Spotify, or Ollama.
