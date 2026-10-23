# Spotify playback investigation (Beta 0.3)

**Question:** Can Veylric control Spotify playback, and what would it take?

**Date:** 22 October 2026 · **Spotify desktop app:** 1.3.6.1921 · **macOS, local only**

## Summary

| Ability | Feasible now? | How | Needs account setup? |
| --- | --- | --- | --- |
| "What's playing?" | Yes | AppleScript reads player state | No |
| Pause, resume, next, previous | Yes | AppleScript commands | No |
| Volume, shuffle, repeat | Yes | AppleScript writable properties | No |
| "Play Adele" (play by name) | Not yet | Web API search for a track ID, then AppleScript `play track` | Yes: a Spotify developer app and credentials |

Basic controls and reading the current track can be built with the same tool Veylric already uses to quit Chrome. Playing something by name is a separate project, because AppleScript can only play a track it is given an exact Spotify ID for.

## Method

1. Read Spotify's scripting dictionary from `/Applications/Spotify.app/Contents/Resources/Spotify.sdef`. (The `sdef` command needs full Xcode, but the dictionary file can be read directly.)
2. Read player properties with `osascript`, each guarded by `if application "Spotify" is running`, so the check never launched Spotify.
3. Did not test play, pause, or skip commands, because they would change playback on the Mac without warning. These are left for a manual test.

## What the dictionary offers

**Commands:** `play`, `pause`, `playpause`, `next track`, `previous track`, `play track <spotify URI>`.

**Readable properties:** `player state` (stopped, playing, or paused), `player position`, and for the `current track`: `name`, `artist`, `album`, `duration`, `id`, `spotify url`, and others.

**Writable properties:** `sound volume` (0–100), `shuffling`, `repeating`, `player position`.

## Findings

1. **Reading state works without changing anything.** Player state, track name, artist, duration, position, volume, shuffle, and repeat all returned correct values while Spotify was paused.
2. **`duration` is in milliseconds, not seconds.** The dictionary says seconds, but a 3:10 track returned `189859`. `player position` really is in seconds (`144.47`). Code must convert duration before reporting it.
3. **Asking about a closed app opens it.** `tell application "Spotify"` launches Spotify if it is not running. Veylric must check `is_app_running("Spotify")` first, or a simple "what's playing?" would have a side effect.
4. **Combining several properties in one script can fail.** One combined script raised `Can't make player position into type real`, while reading the same property on its own worked. Reading properties one at a time, with error handling, is more reliable.
5. **Commands report sending, not outcome.** AppleScript commands such as `pause` return nothing. To verify, Veylric should read `player state` afterwards, matching the attempt-versus-verify pattern used for opening apps.

## Play by name: why it is harder

`play track` needs an exact URI such as `spotify:track:<id>`. The desktop app's search (which Veylric already opens) only shows results on screen; it gives Python no IDs. Getting an ID from a name requires Spotify's Web API:

- Registering a developer app and handling a client ID and secret, which is Veylric's first real credential and needs safe storage outside the code and Git.
- A network request for every search, and agreement to Spotify's developer terms, which should be checked at the time of building because they change.
- The search could match the wrong track, so the model-versus-Python safeguards would need extending to choosing a result.

Recommendation: leave this for a later beta, after the stronger safeguards planned for 0.4.

## Recommended build for Beta 0.3

- **"What's playing?"**: read-only and needs no approval. Report "nothing is playing" when stopped, and never launch Spotify to ask.
- **Pause, resume, next, previous**: low-impact and reversible, so no approval, in line with opening apps. After each command, read `player state` or the track name to verify, and write an action record.
- **Volume, shuffle, and repeat**: possible, but optional for 0.3.
- **Recognise requests** with exact commands first (`pause music`, `next song`), and only then consider extending the classifier with new allowlisted labels.

## Outcome

Decision on play-by-name (22 October 2026): deferred. It is feasible within Spotify's Developer Terms, but it is not needed yet; searching and pressing play on the top result works today.

Notes for revisiting:

- Spotify's 2026 Development Mode rules require the app owner to have Premium (the owner does), limit apps to 5 users, and cap search at 10 results per request.
- Use app-only Client Credentials, which can search the public catalogue but cannot access any user's account.
- Store the Client ID and Secret in the macOS Keychain, typed by the owner in Terminal; never in code, Git, logs, or chat.
- The Developer Terms prohibit "ingesting Spotify Content into a machine learning or AI model". Web API results (titles, artists, IDs) must stay in Python: they may be shown to the user, but action records sent to the language model should use only the user's own words.
- Do not store Web API results beyond the single request, make calls only on explicit requests, and notify Spotify and reset the secret if it is ever exposed.
- Anyone else running Veylric must create their own Spotify app and credentials.
- Reading the terms and accepting them is the owner's decision.

Built in Beta 0.3: "what's playing?" plus pause, resume, next, and previous, using exact phrases or natural requests classified into allowlisted labels. Every AppleScript call includes the "is running" guard, so it cannot launch Spotify. Each control is verified by reading the player state or track ID afterwards. Spotify's `previous track` only restarts a song that is more than about 3 seconds in, so Veylric first sets the position to 0 and then goes back; it reports success only when the track changes. Volume, shuffle, repeat, and play-by-name were not built.
