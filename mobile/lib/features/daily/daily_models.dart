class DailySummary {
  const DailySummary({
    required this.date,
    this.weightKg,
    required this.waterMl,
    required this.foodCalories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.steps,
    this.sleepMinutes,
    required this.workoutSessions,
  });

  factory DailySummary.fromJson(Map<String, Object?> json) {
    return DailySummary(
      date: DateTime.parse(json['date'] as String),
      weightKg: (json['weight_kg'] as num?)?.toDouble(),
      waterMl: json['water_ml'] as int,
      foodCalories: json['food_calories'] as int,
      proteinG: json['protein_g'] as int,
      carbsG: json['carbs_g'] as int,
      fatG: json['fat_g'] as int,
      steps: json['steps'] as int,
      sleepMinutes: json['sleep_minutes'] as int?,
      workoutSessions: json['workout_sessions'] as int,
    );
  }

  final DateTime date;
  final double? weightKg;
  final int waterMl;
  final int foodCalories;
  final int proteinG;
  final int carbsG;
  final int fatG;
  final int steps;
  final int? sleepMinutes;
  final int workoutSessions;
}

class NutritionTarget {
  const NutritionTarget({
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.waterMl,
    this.fiberG = 0,
    this.sodiumMg = 0,
  });

  factory NutritionTarget.fromJson(Map<String, Object?> json) {
    return NutritionTarget(
      calories: json['calories'] as int,
      proteinG: json['protein_g'] as int,
      carbsG: json['carbs_g'] as int,
      fatG: json['fat_g'] as int,
      waterMl: json['water_ml'] as int,
      fiberG: (json['fiber_g'] as int?) ?? 0,
      sodiumMg: (json['sodium_mg'] as int?) ?? 0,
    );
  }

  final int calories;
  final int proteinG;
  final int carbsG;
  final int fatG;
  final int waterMl;
  final int fiberG;
  final int sodiumMg;
}
