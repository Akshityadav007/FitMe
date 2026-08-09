class RecommendedItem {
  const RecommendedItem({
    required this.menuItemId,
    required this.name,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.confidence,
  });

  factory RecommendedItem.fromJson(Map<String, Object?> json) {
    return RecommendedItem(
      menuItemId: json['menu_item_id'] as String,
      name: json['name'] as String,
      calories: json['calories'] as int,
      proteinG: json['protein_g'] as int,
      carbsG: json['carbs_g'] as int,
      fatG: json['fat_g'] as int,
      confidence: (json['confidence'] as num).toDouble(),
    );
  }

  final String menuItemId;
  final String name;
  final int calories;
  final int proteinG;
  final int carbsG;
  final int fatG;
  final double confidence;
}

class MacroTotals {
  const MacroTotals({
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
  });

  factory MacroTotals.fromJson(Map<String, Object?> json) {
    return MacroTotals(
      calories: json['calories'] as int,
      proteinG: json['protein_g'] as int,
      carbsG: json['carbs_g'] as int,
      fatG: json['fat_g'] as int,
    );
  }

  final int calories;
  final int proteinG;
  final int carbsG;
  final int fatG;
}

class Recommendation {
  const Recommendation({
    required this.date,
    required this.mealType,
    required this.targets,
    required this.consumed,
    required this.remaining,
    this.recommendation,
    this.alternatives = const [],
    required this.reason,
    required this.uncertainty,
    this.uncertaintyReason,
    required this.suggestedAction,
  });

  factory Recommendation.fromJson(Map<String, Object?> json) {
    final rawAlternatives = json['alternatives'] as List<Object?>? ?? const [];
    return Recommendation(
      date: DateTime.parse(json['date'] as String),
      mealType: json['meal_type'] as String,
      targets: MacroTotals.fromJson(json['targets'] as Map<String, Object?>),
      consumed: MacroTotals.fromJson(json['consumed'] as Map<String, Object?>),
      remaining: MacroTotals.fromJson(json['remaining'] as Map<String, Object?>),
      recommendation: json['recommendation'] == null
          ? null
          : RecommendedItem.fromJson(json['recommendation'] as Map<String, Object?>),
      alternatives: rawAlternatives
          .map((item) => RecommendedItem.fromJson(item as Map<String, Object?>))
          .toList(),
      reason: json['reason'] as String,
      uncertainty: (json['uncertainty'] as bool?) ?? false,
      uncertaintyReason: json['uncertainty_reason'] as String?,
      suggestedAction: json['suggested_action'] as String,
    );
  }

  final DateTime date;
  final String mealType;
  final MacroTotals targets;
  final MacroTotals consumed;
  final MacroTotals remaining;
  final RecommendedItem? recommendation;
  final List<RecommendedItem> alternatives;
  final String reason;
  final bool uncertainty;
  final String? uncertaintyReason;
  final String suggestedAction;
}
