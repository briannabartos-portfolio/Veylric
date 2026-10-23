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

## Spotify search commands

- search spotify
- search spotify for
- search spotify for Fleetwood Mac

## Current limitations

- AI tool selection supports Spotify opening only.
- Time and date questions use a fixed phrase list.
- Spotify search uses defined command formats.
- Search opens results; it does not request playback.
- Model classifications and conversational replies can be wrong.
- Confirmation and file safeguards are enforced by Python.

## Working files

- main.py: assistant loop, conversation, and existing tools.
- intent_test.py: request classifier and standalone classification test.
- spotify_search_test.py: reusable search function and standalone search test.