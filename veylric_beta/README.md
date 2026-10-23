# Veylric Beta

A personal assistant inspired by JARVIS, built while learning Python.

## Current abilities

- Preview file organization in a practice folder.
- Open Spotify, Chrome, and Messages.
- Request Chrome to quit.
- Move one specific test file after explicit approval.
- Organize recognized practice files after approval.
- Chat through Ollama using Ministral 3 8B.
- Report an Ollama connection failure without ending the session.
- Display AI replies progressively using streaming.
- Retain the latest five completed chat exchanges during a session.
- Clear session history with `clear conversation`.
- Report Ollama response errors without ending the session.

## Safeguards

- `organize my files` and `organise my files` preview without moving files.
- `move practice files` attempts real moves only after explicit approval.
- Unknown file types are flagged for review.
- File actions require the exact approval word APPROVE.
- Missing sources and occupied destinations are skipped.
- The real move uses macOS overwrite protection.
- No deletion capability is implemented.

## Tests completed

- Approval and cancellation.
- Empty and missing practice folders.
- Uppercase file extensions.
- Existing destination file.
- Source renamed while awaiting approval.
- Successful real move and repeated request afterward.
- Streamed replies without duplicate output.
- Recall within a session and reset after restarting.
- Explicit conversation clearing.
- Preserve chat capitalization while matching commands case-insensitively.
- Ollama connection failure, missing model, and recovery.

## Beta 0.2 additions

- Interpret natural requests to open Spotify.
- Validate model-selected labels against an allowlist.
- Require OPEN confirmation for model-selected Spotify opening.
- Ask for clarification on ambiguous Spotify requests.
- Resolve “open it” and “launch it” using one-turn Spotify context.
- Summarize real file actions with moved, skipped, and failed counts.
- Search Spotify after previewing the search words and receiving SEARCH approval.

## Beta 0.3 additions (in progress)

- Run clear Spotify opening requests without a second confirmation.
- Only consult the classifier when a message mentions Spotify.
- Verify that Spotify is running after opening it, and report already-open, verified, or unconfirmed outcomes.
- Quit Chrome only if it is running.
- Answer time and date questions from the Mac's clock.
- Give conversational replies the current date and time.
- Understand natural Spotify search requests and extract the search words.
- Drop any search words the model invented; ask for SEARCH approval when that happens.
- Run normal searches without approval and verify that Spotify is running.
- Remember the last search for the session; `search it again` repeats it and `clear conversation` forgets it.
- Treat "search for X" after Spotify clarification as a Spotify search.
- Resolve "them" and "that" from the conversation, checking whether the words came from the user, earlier messages, or Veylric's own replies.
- Ask for SEARCH approval when search words came only from Veylric's replies.
- Add action records for tool outcomes (apps, searches, files, time, date) so chat can answer questions about what happened.
- Keep five exchanges plus their action records, capped at 20 entries.
- Report what's playing and pause, resume, skip, or go back in Spotify, verified by reading the player state afterwards.
- Guard every Spotify AppleScript call so it can never launch Spotify.
- Classify natural playback requests (pause, resume, next, previous, what's playing) and song requests that do not name Spotify.
- Strip Markdown such as **label** from classifier replies before the exact allowlist check.
- Tell the chat model it cannot act in its reply, so it does not claim to have paused or played anything.

## Beta 0.3 tests

- Open Spotify while closed: reported as verified.
- Open Spotify while already open: reported as already open.
- Time and date phrases, including a curly apostrophe, answered by Python.
- "What time does the shop close" sent to conversation, not the clock.
- Natural search extraction for artists, songs, podcasts, and moods.
- Invented words ("Folklore Evermore") removed and SEARCH approval triggered.
- Cancelled and mistyped approvals do not open Spotify.
- Repeat search before any search, after a search, and after clearing the conversation.
- "Search for them" after Veylric named Fleetwood Mac: SEARCH approval requested.
- "Find them" after the user mentioned Lorde: searched directly with a note.
- "Shake It Off" treated as a title, not a reference.
- "My friend recommended Lorde, find them on spotify" uses the name in the same message, not an earlier one.
- A wrong chat answer (Fiona Apple for "Dreams") was caught by the SEARCH check when searched for.
- "Did that work?" and "What did you search for?" answered from action records.
- "Did you open Chrome?" with no record: Veylric says it has no record.
- Unconfirmed Spotify opening: Veylric does not claim success.
- "Is that late?" after asking the time uses the recorded time.
- What's playing read from the real Spotify without changing playback; "pause" while paused sends nothing.
- Simulated Spotify: resume, skip, back, and pause verified.
- Real Spotify: "previous song" a few seconds into a track restarted it (Spotify's own rule), so Veylric now rewinds to the start first and then goes back; only a track change counts as verified.
- Simulated broken commands reported as not confirmed; closed Spotify received no commands.
- Previous-track race reproduced with a delayed simulation and fixed by checking the position before the command.
- 54/54 classifier checks across two runs, including "Play Sawadika by LISA", "Could you pause my music for me?", and traps such as "Should I skip breakfast?" and "Did you pause the music earlier?".
- A natural pause request that previously produced a false "I've paused the music" now runs the verified control.

## Spotify search commands

- search spotify
- search spotify for
- search spotify for Fleetwood Mac

## Current limitations

- AI tool selection supports Spotify opening only.
- Time and date questions use a fixed phrase list.
- Spotify search uses defined command formats.
- Search opens results; it does not play a song by name.
- Model classifications and conversational replies can be wrong.
- Confirmation and file safeguards are enforced by Python.

## Working files

- main.py: assistant loop, conversation, and existing tools.
- intent_test.py: request classifier and standalone classification test.
- spotify_search_test.py: reusable search function and standalone search test.