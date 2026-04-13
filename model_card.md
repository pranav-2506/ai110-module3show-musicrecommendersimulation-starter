# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

**Intended use:** VibeFinder 1.0 suggests up to five songs from an 18-song catalog based on a listener's preferred genre, mood, energy level, and musical positivity (valence). It is designed for classroom exploration only — to demonstrate how content-based filtering works in a simple, fully transparent way. The intended audience is students learning about AI recommender systems.

**Non-intended use:** This system should not be used as a real music discovery product. It is not designed to serve actual listeners, handle large catalogs, or replace services like Spotify or Apple Music. It should not be used to make decisions that affect real users, monetize recommendations, or draw conclusions about what music any real population of people enjoys. Because the catalog is tiny and hand-picked, results do not generalize beyond the classroom context.

---

## 3. How the Model Works

Think of VibeFinder like a judge who listens to a description of what you want and then scores every song in the room against that description.

For each song, the judge awards bonus points if the song's **mood** matches yours (biggest bonus — getting the emotional vibe right matters most), and more points if the **genre** matches. Then the judge looks at the numbers: how close is the song's **energy** to your target? How similar is its **positivity** (valence)? The closer the match, the more points.

Once every song has a score, the judge sorts them from highest to lowest and hands you the top five — skipping any artist who already appeared in the list so you don't get five songs from the same person.

The whole process is transparent: every point in the score comes from a specific feature match, so you can always trace exactly why a song was recommended.

---

## 4. Data

The catalog contains **18 songs** across 15 distinct genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, r&b, classical, hip-hop, edm, metal, folk, blues, dream pop) and 14 distinct moods (happy, chill, intense, relaxed, focused, moody, romantic, melancholic, energetic, euphoric, angry, nostalgic, sad, dreamy).

The dataset was provided as a starter CSV and lightly expanded. It over-represents the chill/lofi space (4 of 18 songs have low energy and relaxed moods) and under-represents harder genres — there is only one metal song, one blues song, and one classical song. Most songs were chosen to illustrate a range of genres, not to reflect the actual distribution of what people listen to. Whose taste it reflects is unclear — it skews Western and English-language.

---

## 5. Strengths

The system works best when the user's preferences are internally consistent — for example, a lofi/chill/low-energy listener gets Library Rain and Midnight Coding at the top with scores near 9.0 out of 10.5, which genuinely feels right. It is also fully explainable: every recommendation comes with a plain-English reason ("mood match (+2.5), energy proximity (+2.94)"), which makes it easy to understand and debug. Mood being weighted highest (2.5) means the system consistently surfaces songs that match the emotional intent, even across genre boundaries — a chill ambient track can surface for a lofi listener, which is often the right call.

---

## 6. Limitations and Bias

**The biggest weakness discovered through testing is the mood-energy conflict in edge cases.** When a user asks for something "sad" but also "high-energy" (Profile 4), the system splits: it ranks a low-energy blues song first (because the mood matches) while ranking a high-energy EDM song second (because the genre and energy match). Neither result fully satisfies the user, but the system has no way to recognize that the preferences are in tension — it just adds up the points.

**Energy dominates numeric scoring.** Energy carries 3.0 of a maximum 10.5 points (~29%), more than any other feature. When we doubled the energy weight in the experiment, the rankings barely changed — the same songs stayed on top — which reveals that energy is already the primary driver. Songs that match energy closely will always score well, even if their mood or genre is wrong.

**The catalog is too small and unbalanced to serve all users fairly.** There is one metal song, one blues song, and one classical song. A user who wants classical recommendations will always get Velvet Underground Suite as their top result, with no meaningful alternatives — the system is forced to pad the list with energy-adjacent songs from completely different genres.

**The system treats all users as having a single, fixed taste.** It cannot learn that a user skips sad songs, favors live recordings, or always plays high-energy music on Monday mornings. Every session starts from scratch.

---

## 7. Evaluation

Four user profiles were tested:

| Profile | Top Result | Surprise? |
|---|---|---|
| High-Energy Pop (genre=pop, mood=happy, energy=0.8) | Sunrise City — 8.86/10.5 | No — perfect match on all four signals |
| Chill Lofi Study (genre=lofi, mood=chill, energy=0.35) | Library Rain — 9.00/10.5 | No — the dataset has good lofi coverage |
| Intense Rock Workout (genre=rock, mood=intense, energy=0.92) | Storm Runner — 8.81/10.5 | Gym Hero (#2) is a pop song — it ranked high because it matched "intense" mood and had near-identical energy |
| Edge Case — High-Energy + Sad (genre=edm, mood=sad, energy=0.95) | Blue Smoke (blues) — 5.79 | Yes — a slow blues song ranked first for someone who wanted high-energy EDM, purely because mood match outweighed energy mismatch |

The most revealing experiment was the **weight shift**: doubling energy (3.0 → 6.0) and halving genre (1.5 → 0.75) on the pop/happy profile. The ranking order did not change, but the gap between scores widened and Drop the Horizon (EDM, no mood/genre match) jumped into the top 5, replacing Golden Hour. This confirmed that energy was already the dominant signal at default weights — amplifying it further just made that dominance more visible.

---

## 8. Future Work

- **Handle conflicting preferences explicitly.** If a user's mood and energy are on opposite ends of the emotional spectrum (e.g., sad + high-energy), the system should warn the user or split the list into "mood-first" and "energy-first" halves rather than silently producing a confused result.
- **Balance catalog representation before scoring.** A fairer system would ensure that every genre has at least three or four songs so niche-genre users get real variety in their top-five.
- **Add a listening history signal.** Even tracking which genres appeared in the last session would allow the system to nudge recommendations toward something new, reducing the filter-bubble effect.
- **Support range preferences.** Instead of `energy: 0.8`, allow `energy_min: 0.7, energy_max: 0.9` so the scoring rewards being *within* a comfort zone rather than just being *close* to a single target.

---

## 9. Personal Reflection

Building VibeFinder made it clear how much is hidden inside a single number. When Spotify says "you might like this," it has collapsed millions of data points — your play history, other listeners' behavior, the audio waveform itself — into a recommendation. This simulation only uses six features and 18 songs, and it already produces surprising results like a blues song surfacing for someone who wanted high-energy EDM. That gap between "what the user asked for" and "what the math decided" is where bias and unfairness live in real systems too — just at a much larger scale and with much less transparency.

The experiment also changed how I think about weight tuning. It felt like a small change (doubling one number), but it shifted the philosophical question the system was answering — from "what song fits this person's vibe?" to "what song has the right energy?" Human judgment still matters here because no algorithm can decide which question is worth asking.
