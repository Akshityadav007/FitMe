class WeightEntry {
  const WeightEntry({required this.date, required this.weightKg});

  factory WeightEntry.fromJson(Map<String, Object?> json) {
    return WeightEntry(
      date: DateTime.parse(json['date'] as String),
      weightKg: (json['weight_kg'] as num).toDouble(),
    );
  }

  final DateTime date;
  final double weightKg;
}

class WeightSummary {
  const WeightSummary({
    this.entries = const [],
    this.sevenDayAverageKg,
    this.trendKg,
    this.rateOfChangeKgPerWeek,
  });

  factory WeightSummary.fromJson(Map<String, Object?> json) {
    final rawEntries = json['entries'] as List<Object?>? ?? const [];
    return WeightSummary(
      entries: rawEntries
          .map((entry) => WeightEntry.fromJson(entry as Map<String, Object?>))
          .toList(),
      sevenDayAverageKg: (json['seven_day_average_kg'] as num?)?.toDouble(),
      trendKg: (json['trend_kg'] as num?)?.toDouble(),
      rateOfChangeKgPerWeek: (json['rate_of_change_kg_per_week'] as num?)?.toDouble(),
    );
  }

  final List<WeightEntry> entries;
  final double? sevenDayAverageKg;
  final double? trendKg;
  final double? rateOfChangeKgPerWeek;
}

class NutritionSummary {
  const NutritionSummary({
    this.daysLogged = 0,
    this.averageCalories,
    this.averageProteinG,
    this.proteinAdherencePercent,
  });

  factory NutritionSummary.fromJson(Map<String, Object?> json) {
    return NutritionSummary(
      daysLogged: json['days_logged'] as int,
      averageCalories: json['average_calories'] as int?,
      averageProteinG: json['average_protein_g'] as int?,
      proteinAdherencePercent: json['protein_adherence_percent'] as int?,
    );
  }

  final int daysLogged;
  final int? averageCalories;
  final int? averageProteinG;
  final int? proteinAdherencePercent;
}

class HydrationSummary {
  const HydrationSummary({
    this.daysLogged = 0,
    this.averageWaterMl,
    this.waterAdherencePercent,
  });

  factory HydrationSummary.fromJson(Map<String, Object?> json) {
    return HydrationSummary(
      daysLogged: json['days_logged'] as int,
      averageWaterMl: json['average_water_ml'] as int?,
      waterAdherencePercent: json['water_adherence_percent'] as int?,
    );
  }

  final int daysLogged;
  final int? averageWaterMl;
  final int? waterAdherencePercent;
}

class StepsSummary {
  const StepsSummary({this.daysLogged = 0, this.averageSteps});

  factory StepsSummary.fromJson(Map<String, Object?> json) {
    return StepsSummary(
      daysLogged: json['days_logged'] as int,
      averageSteps: json['average_steps'] as int?,
    );
  }

  final int daysLogged;
  final int? averageSteps;
}

class SleepSummary {
  const SleepSummary({this.daysLogged = 0, this.averageSleepMinutes});

  factory SleepSummary.fromJson(Map<String, Object?> json) {
    return SleepSummary(
      daysLogged: json['days_logged'] as int,
      averageSleepMinutes: json['average_sleep_minutes'] as int?,
    );
  }

  final int daysLogged;
  final int? averageSleepMinutes;
}

class TrainingSummary {
  const TrainingSummary({this.workoutDays = 0, this.trainingAdherencePercent});

  factory TrainingSummary.fromJson(Map<String, Object?> json) {
    return TrainingSummary(
      workoutDays: json['workout_days'] as int,
      trainingAdherencePercent: json['training_adherence_percent'] as int?,
    );
  }

  final int workoutDays;
  final int? trainingAdherencePercent;
}

class WeeklyProgress {
  const WeeklyProgress({
    required this.endDate,
    required this.startDate,
    required this.days,
    required this.weight,
    required this.nutrition,
    required this.hydration,
    required this.steps,
    required this.sleep,
    required this.training,
  });

  factory WeeklyProgress.fromJson(Map<String, Object?> json) {
    return WeeklyProgress(
      endDate: DateTime.parse(json['end_date'] as String),
      startDate: DateTime.parse(json['start_date'] as String),
      days: json['days'] as int,
      weight: WeightSummary.fromJson(json['weight'] as Map<String, Object?>),
      nutrition: NutritionSummary.fromJson(json['nutrition'] as Map<String, Object?>),
      hydration: HydrationSummary.fromJson(json['hydration'] as Map<String, Object?>),
      steps: StepsSummary.fromJson(json['steps'] as Map<String, Object?>),
      sleep: SleepSummary.fromJson(json['sleep'] as Map<String, Object?>),
      training: TrainingSummary.fromJson(json['training'] as Map<String, Object?>),
    );
  }

  final DateTime endDate;
  final DateTime startDate;
  final int days;
  final WeightSummary weight;
  final NutritionSummary nutrition;
  final HydrationSummary hydration;
  final StepsSummary steps;
  final SleepSummary sleep;
  final TrainingSummary training;
}
