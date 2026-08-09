# FitMe Product Specification

## 1. Product vision

FitMe is a personal fitness operating system for one primary user
initially. It records daily health and fitness events, calculates
deterministic nutrition/progress metrics, and uses an AI coach to
interpret current state and provide actionable recommendations.

The user should not need to manually calculate calories, macros,
hydration, or weekly trends.

The user tells the app what happened. The app maintains state. The coach
tells the user what to do next.

## 2. Product principles

### 2.1 Facts before AI

The application database is the source of truth for:

-   User profile
-   Targets
-   Food
-   Nutrition
-   Water
-   Weight
-   Sleep
-   Steps
-   Workout logs
-   Office menus
-   Daily summaries

The LLM must not be the source of truth.

### 2.2 Deterministic calculations stay deterministic

Do not ask the LLM to calculate:

-   Calories consumed
-   Remaining calories
-   Protein consumed
-   Remaining protein
-   Macro totals
-   Water totals
-   Weight averages
-   Weight trend
-   Rate of weight change
-   BMI
-   Any other arithmetic that the backend can calculate reliably

The backend performs these calculations.

### 2.3 AI handles interpretation

Use the AI for:

-   Meal recommendations
-   Explaining tradeoffs
-   Interpreting daily context
-   Coaching
-   Natural-language interaction
-   Identifying practical patterns
-   Turning structured data into useful advice

### 2.4 Minimize user effort

The user should be able to say things like:

> "I had two eggs and black coffee."

or:

> "Dinner was 180g chicken, two rotis and curd."

The application should turn this into structured data with confirmation
where uncertainty is material.

## 3. Daily lifecycle

### Morning

Show:

-   Greeting
-   Current weight if entered
-   Yesterday's summary
-   Today's calorie target
-   Today's protein target
-   Today's hydration target
-   Today's training status
-   Key coaching note

Allow:

-   Weight entry
-   Sleep entry
-   Pre-workout food/drink logging
-   Water logging

### Workout

The workout program belongs to the real trainer.

FitMe may record:

-   Workout name/type
-   Start time
-   End time
-   Duration
-   Exercises performed
-   Sets/reps/weight if the user wants to log them
-   Cardio duration
-   Cardio parameters
-   Notes
-   Perceived exertion

The MVP should not require detailed exercise-by-exercise entry. Provide
a lightweight workflow first.

### Office breakfast

The user uploads a photograph of the office menu/food information.

The system:

1.  Stores the image.
2.  Runs image understanding/OCR extraction.
3.  Extracts food names and nutrition values when visible.
4.  Normalizes food names.
5.  Attempts to match against known foods.
6.  Creates/updates the day's breakfast menu.
7.  Shows extracted information for user confirmation when confidence is
    low.

The same flow applies to lunch and snacks.

### Meal recommendation

Given the current daily state and available office menu, the coach
should recommend combinations that help the user meet:

-   Remaining calories
-   Remaining protein
-   Remaining macros
-   Dietary preference
-   User dislikes
-   Meal context
-   Training/recovery context

The coach should prefer simple recommendations rather than dumping a
large list of options.

### Dinner

Dinner may be:

-   Manually logged
-   Selected from known foods
-   Entered in natural language
-   Photographed and interpreted

The coach can recommend dinner based on remaining daily targets.

### Hydration

The app tracks water entries.

It should display:

-   Consumed today
-   Target
-   Remaining
-   Progress

The app may generate reminders based on time and current hydration
progress.

Avoid excessive notifications.

### Sleep

MVP:

-   Manual bedtime
-   Manual wake time
-   Calculated duration
-   Optional subjective quality

Future:

-   Apple Health
-   Google Health Connect
-   Wearables

The data model must abstract the source so future integrations do not
require redesigning the sleep domain.

## 4. Food/menu image processing

The user expects to upload a food/menu photograph every day.

The system should support:

-   Image upload
-   OCR/vision extraction
-   Food normalization
-   Nutrition extraction
-   Duplicate/repeated food detection
-   User confirmation
-   Persistence

### Repeated food detection

Start simple:

1.  Normalize extracted food names.
2.  Exact match.
3.  Case-insensitive match.
4.  Normalized whitespace/punctuation.
5.  Fuzzy string matching.
6.  Only later introduce embeddings if real data shows they are
    necessary.

If a known food is repeated, reuse trusted stored nutrition information
instead of asking the model to infer it again.

Never silently overwrite trusted nutrition data with a lower-confidence
extraction.

## 5. AI coach

The coach must have access to structured current state.

Example context:

``` json
{
  "user": {
    "age": 27,
    "sex": "male",
    "height_cm": 181,
    "weight_kg": 82.7,
    "goal": "recomposition"
  },
  "targets": {
    "calories": 2350,
    "protein_g": 175,
    "fat_g": 70,
    "carbs_g": 260,
    "water_ml": 3000
  },
  "today": {
    "calories_consumed": 1420,
    "protein_g": 121,
    "fat_g": 48,
    "carbs_g": 172,
    "water_ml": 1900,
    "steps": 4821
  },
  "remaining": {
    "calories": 930,
    "protein_g": 54,
    "fat_g": 22,
    "carbs_g": 88,
    "water_ml": 1100
  }
}
```

The exact schema may evolve, but the concept must remain.

## 6. Coach tools

The AI orchestration layer should expose controlled tools/functions such
as:

-   `get_user_profile`
-   `get_today_summary`
-   `get_remaining_targets`
-   `get_today_menu`
-   `get_recent_weight_trend`
-   `get_recent_training`
-   `get_recent_sleep`
-   `log_food`
-   `log_water`
-   `log_weight`
-   `log_sleep`
-   `log_workout`
-   `recommend_meal`

The model must not have unrestricted database access.

Tool calls must be validated server-side.

## 7. Proactive coaching

The app should proactively surface useful information without requiring
a question.

Examples:

### Hydration

"You've had 800 ml today against a 3 L target. Have another 400--500
ml."

### Protein

"You're at 91g protein and need approximately 84g more. Make the next
meal protein-heavy."

### Dinner

"You have \~680 kcal remaining. A chicken + roti + vegetables + curd
dinner fits well."

### End of day

"Calories: 2281/2350. Protein: 174/175g. Water: 3.0/3.0L. Strong day."

These are examples only. The application should generate them from
structured state.

## 8. Weekly review

Provide:

-   Average calorie intake
-   Average protein
-   Water adherence
-   Average steps
-   Training adherence
-   Average sleep
-   Weight change
-   Weight trend
-   Estimated rate of loss/gain
-   Coach observations
-   One or two priorities for the next week

Do not overreact to a single weigh-in.

## 9. Nutrition adjustment logic

Initial target is approximately 2350 kcal/day.

The system should not automatically change targets based on a single
day.

Target adjustments should consider:

-   At least 2--3 weeks of data
-   Average calorie intake
-   7-day or equivalent weight trend
-   Adherence
-   Training performance if available

Target adjustment should be explainable and preferably require user
confirmation in the MVP.

## 10. Rest day

Friday is the rest day.

Initial policy:

-   Same calorie target
-   Same protein target
-   Same macro targets unless otherwise configured

Do not create an arbitrary "starve on rest day" rule.

## 11. Dietary rules

User dietary preference:

-   Eggetarian + chicken
-   Spicy food not preferred

Regularly acceptable foods include:

-   Eggs
-   Chicken
-   Paneer
-   Curd
-   Greek yogurt
-   Whey
-   Soy/tofu
-   Dal

The system should not recommend spicy food as a default.

## 12. Safety

The app must not:

-   Diagnose medical conditions
-   Present medical advice as professional diagnosis
-   Prescribe medications
-   Recommend dangerous calorie restriction
-   Encourage dehydration
-   Replace a medical professional
-   Replace the user's real trainer
-   Invent nutrition facts when source information is available but
    uncertain

When nutrition information is uncertain, explicitly state uncertainty
and ask for confirmation when necessary.

## 13. MVP screens

Minimum screens:

1.  Splash/loading
2.  Authentication
3.  Home/Daily dashboard
4.  Food logging
5.  Office menu capture
6.  Meal/menu details
7.  Water tracking
8.  Workout logging
9.  Sleep logging
10. Weight logging
11. AI Coach
12. Daily summary
13. Weekly progress
14. Profile/settings

Avoid adding social features, gamification, community feeds, or
unnecessary features in MVP.

## 14. Future features

Potential future scope:

-   Apple Health
-   Google Health Connect
-   Wearables
-   Automatic steps
-   Automatic sleep
-   Heart rate/recovery
-   Progress photos
-   Body composition history
-   Barcode scanning
-   More advanced food recognition
-   Personalized maintenance estimation
-   Multi-user support
-   Trainer portal
