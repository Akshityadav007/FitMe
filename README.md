# FitMe

FitMe is a Flutter mobile application backed by FastAPI and PostgreSQL
that acts as an AI-assisted nutrition, hydration, recovery, and
fitness-adherence coach.

The application is built around a simple principle:

> The application owns facts and deterministic calculations. The AI
> interprets those facts and coaches the user.

## Current user profile

-   Age: 27
-   Sex: Male
-   Height: 181 cm
-   Weight: 82.7 kg
-   Body fat: 24.5%
-   Visceral fat: 9
-   Muscle: 32.8%
-   BMI: 25.2
-   Goal: body recomposition
-   Diet: eggetarian + chicken
-   Spicy food: not preferred
-   Activity: desk job, approximately 3--5k steps/day
-   Training: heavy resistance training; workout program is provided by
    a real trainer and must not be replaced by the AI
-   Cardio: currently approximately 20 minutes treadmill, 4.5 km/h, 10%
    incline
-   Rest day: Friday
-   Wake: \~06:00
-   Gym: \~06:30--09:30
-   Work: \~10:00--10:30 to \~17:00--18:00
-   Lunch: \~13:00--13:30
-   Snack: \~16:00--18:00
-   Dinner: \~19:00--21:00
-   Sleep: \~22:00--23:00
-   Water: currently \~2--3 L/day
-   Pre-workout: half cup black coffee
-   Optional evening drink: half cup tea
-   Office provides breakfast, lunch, and snacks
-   Dinner is self-cooked or prepared by a maid
-   User currently tracks sleep manually; future
    wearable/health-platform integration is planned
-   User currently uses whey protein isolate
-   No stated medical conditions, food allergies, or medication
    constraints

## Initial nutrition targets

These are starting targets, not permanent truths:

-   Calories: \~2350 kcal/day
-   Protein: \~175 g/day
-   Fat: \~70 g/day
-   Carbohydrates: \~260 g/day
-   Water: \~2.5--3.5 L/day
-   Steps: gradually work toward \~7--8k/day

The app must treat these as configurable targets stored in the database.
Do not hardcode them into prompts or business logic.

The 1810 kcal "maintenance/RM" value reported by the user's
body-composition device must not be treated as authoritative
maintenance. The application should eventually estimate actual
maintenance from longitudinal weight and intake data.

## Primary user experience

The user should be able to:

1.  Start the day and see current targets.
2.  Log pre-workout intake.
3.  Log workout activity.
4.  Upload photographs of office food/menu information.
5.  Have the system extract food and nutrition information.
6.  Receive recommendations about what to eat from the available
    options.
7.  Log consumed food.
8.  Log water.
9.  Log weight.
10. Log sleep manually.
11. Log steps manually initially.
12. Log dinner manually or by photograph.
13. Ask the AI coach questions about the current day.
14. Receive proactive coaching and reminders.
15. Review daily and weekly progress.

## Important product boundary

FitMe is a nutrition/recovery/adherence coach.

It is NOT a replacement for the user's real trainer.

The AI must not invent, modify, or prescribe the user's
resistance-training program unless the user explicitly asks for general
information and the response is clearly framed as informational. The
existing trainer's workout plan remains authoritative.

## Engineering principle

Do not build a chatbot with a database attached.

Build a structured fitness application with an AI coach on top.
