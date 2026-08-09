class MenuImage {
  const MenuImage({
    required this.id,
    required this.userId,
    required this.source,
    required this.status,
    required this.imageUrl,
  });

  factory MenuImage.fromJson(Map<String, Object?> json) {
    return MenuImage(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      source: json['source'] as String,
      status: json['status'] as String,
      imageUrl: json['image_url'] as String,
    );
  }

  final String id;
  final String userId;
  final String source;
  final String status;
  final String imageUrl;
}

class MenuImageItem {
  const MenuImageItem({
    required this.id,
    required this.menuImageId,
    required this.name,
    required this.estimatedCalories,
    required this.estimatedProteinG,
    required this.estimatedCarbsG,
    required this.estimatedFatG,
    required this.confidence,
  });

  factory MenuImageItem.fromJson(Map<String, Object?> json) {
    return MenuImageItem(
      id: json['id'] as String,
      menuImageId: json['menu_image_id'] as String,
      name: json['name'] as String,
      estimatedCalories: json['estimated_calories'] as int,
      estimatedProteinG: json['estimated_protein_g'] as int,
      estimatedCarbsG: json['estimated_carbs_g'] as int,
      estimatedFatG: json['estimated_fat_g'] as int,
      confidence: (json['confidence'] as num).toDouble(),
    );
  }

  final String id;
  final String menuImageId;
  final String name;
  final int estimatedCalories;
  final int estimatedProteinG;
  final int estimatedCarbsG;
  final int estimatedFatG;
  final double confidence;
}

class MenuImageProcess {
  const MenuImageProcess({
    required this.id,
    required this.status,
    required this.items,
  });

  factory MenuImageProcess.fromJson(Map<String, Object?> json) {
    final rawItems = json['items'] as List<Object?>? ?? const [];
    return MenuImageProcess(
      id: json['id'] as String,
      status: json['status'] as String,
      items: rawItems
          .map((item) => MenuImageItem.fromJson(item as Map<String, Object?>))
          .toList(),
    );
  }

  final String id;
  final String status;
  final List<MenuImageItem> items;
}
