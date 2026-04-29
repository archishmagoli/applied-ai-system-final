# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
I centered my design around the core user actions necessary for the application. In this case, a user should be able to perform the following actions:
- Add pet information
- Schedule tasks (e.g. walk the pet, bath time, etc.)
- View the daily schedule of tasks

- What classes did you include, and what responsibilities did you assign to each?

I believe the application should have the following classes and associated attributes/methods. In general, the `Task` class holds the associated methods for creating a task, and each `Pet` will have a list of tasks it needs to get done on its behalf:
### `Owner`
- **Attributes:** `name`, `pets: list[Pet]`, `available_time: int` (minutes/day)
- **Methods:** `add_pet(pet)`, `remove_pet(name)`, `get_pet(name)`

### `Pet`
- **Attributes:** `name`, `age`, `species`, `tasks: list[Task]`
- **Methods:** `add_task(task)`, `remove_task(name)`, `get_tasks()`

### `Task`
- **Attributes:** `name`, `duration: int` (minutes), `priority: str`, `category: str`, `start_time: str | None`
- **Methods:** none — plain data object

### `Schedule`
- **Attributes:** `date`, `pet: Pet`, `available_time: int`, `tasks: list[Task]`
- **Methods:** `generate_plan()`, `display_plan()`

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, my design **did change** during implementation. When I let Claude (via Copilot) take the reins in class design once I had given it a rough idea of what classes, methods, and attributes I was looking for, Claude suggested having **five** classes, with the additional fifth class being for `ScheduledTask`s. I felt this was somewhat redundant, since we already had a `Task` class we could just expand during scheduling, so I suggested we remove that class and stick with the four we have above. Additionally, I initially had each `Owner` own the list of tasks generated, but then that would be difficult to categorize per animal, so I asked Claude to move that ownership to each `Per` instead. This allows for categorization while still allowing us to group by `Owner` via the `Owner has multiple Pets` relationship.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considered two constraints: 
- available time (the owner's daily minute budget, split evenly across pets)
- task priority (high / medium / low)

Obviously, **available time** had to be considered because if the owner can't perform all the tasks on the schedule in a given day, then we didn't do our job properly -- time is the strict cutoff. **Priority** also had to be considered because there may be days the owner's availability doesn't cover the task durations. Tasks are sorted by priority before being packed into the schedule, and any task that doesn't fit in the remaining time is dropped entirely.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler uses an `O(n²)` algorithm for `detect_conflicts()` - meaning that it compares every pair of tasks to ensure the timing doesn't overlap. That tradeoff is reasonable for this scenario because we have a relatively small number of pets and tasks, per our demo in `main.py`. 
Claude suggested that a production scheduler with hundreds of tasks per day would use a sweep-line algorithm (sort by start time, check only adjacent intervals) to bring this down to `O(n log n)`. The simpler `O(n²)` version was kept because the readability gain outweighs any performance need at this scale.
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used throughout the entire project lifecycle - design brainstorming, code implementation, refactoring, debugging, and even testing. I found specific and measurable prompts to be the most helpful - the more direct and detailed I was with Claude, the better it performed. For example, "Fix all bugs in this file" was not as helpful as "Fix the `detect_conflicts()` function to ensure a warning is outputted when overlapping tasks are detected."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
Early in the project, Claude suggested adding a separate `ScheduledTask` class to represent a task that had been assigned a time slot. I pushed back and we talked through whether that was actually necessary. I considered what a `ScheduledTask` would add, which is essentially just a `start_time` field. I realized that `Task` already handled everything needed. Adding a whole new class just to hold one extra field would create redundancy: two classes representing the same concept, with logic split between them for no real benefit. I decided to keep `start_time` as an optional field directly on `Task`, which kept the design simpler and the codebase easier to follow. Claude updated the design to match that decision rather than the other way around.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested five behaviors: chronological sorting, unscheduled task ordering, daily recurrence via `Task.mark_complete()` directly, daily recurrence via `Pet.complete_task()` (the higher-level path), conflict detection on overlapping tasks, and a no-false-positives check for back-to-back tasks.

These tests mattered because they target the three places the system can silently produce wrong output — a schedule that's out of order, a recurring task that doesn't regenerate, or a conflict that goes undetected. Unlike a crash, those failures would just show incorrect data with no error message, which would be immediately obvious to anyone expecting ordered output.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

As I mentioned in the README, I would give a 4 out of 5 confidence rating for the scheduler. The core logic is well-covered with tests: every major function has at least one positive case and one edge case. I also added multiple tests for the sorting and filtering algorithms I implemented. If I had more time, I would probably test the `build_owner_schedules` integration path (owner → pets → schedules in one call),
weekly recurrence (only daily is tested), and `generate_plan`'s time-budget enforcement — verifying that a task which doesn't fit is actually dropped. Those aren't risky omissions for this scale of project, but they're the natural next tests to write.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm really satisfied with the AI interactions I had in this project. I felt almost totally in sync with Claude, and I liked how the final product turned out, especially compared to the first `Show` project we had to complete.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
As mentioned in the README, I would probably add integration-level testing of the full `build_owner_schedules` flow and the Streamlit UI layer. A lot of the testing I currently have is pretty surface-level/adherent to the exact instructions in the project description. I would also to try to simplify the demo layout; I think it is readable so far but having more of a structure to things would make it even clearer. Lastly, I would update the application's design such that it outputs the scheduling conflcit warning during task creation instead of running it separately.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I keep learning this, but honestly AI's main capability and intelligence comes from the thoroughness and correctness of the prompts you use. I've realized time and time again that vague prompts with bland instructions don't help any AI agent come up with a beautiful finished product, and you must be intelligent enough to navigate the requirements in order to build something meaningful.