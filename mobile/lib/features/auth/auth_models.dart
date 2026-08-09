class UserSummary {
  const UserSummary({
    required this.id,
    required this.email,
    this.firstName,
    this.lastName,
    this.goal,
    this.activityLevel,
    this.dietaryPreferences,
  });

  factory UserSummary.fromJson(Map<String, dynamic> json) {
    return UserSummary(
      id: json['id'] as String,
      email: json['email'] as String,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      goal: json['goal'] as String?,
      activityLevel: json['activity_level'] as String?,
      dietaryPreferences: json['dietary_preferences'] as String?,
    );
  }

  final String id;
  final String email;
  final String? firstName;
  final String? lastName;
  final String? goal;
  final String? activityLevel;
  final String? dietaryPreferences;
}

class AuthResponse {
  const AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.user,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'] as String,
      tokenType: (json['token_type'] ?? 'bearer') as String,
      user: UserSummary.fromJson(json['user'] as Map<String, dynamic>),
    );
  }

  final String accessToken;
  final String tokenType;
  final UserSummary user;
}

class UserProfile {
  const UserProfile({
    required this.id,
    required this.userId,
    this.firstName,
    this.lastName,
    this.age,
    this.sex,
    this.weightKg,
    this.heightCm,
    this.goal,
    this.activityLevel,
    this.dietaryPreferences,
    this.notes,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      firstName: json['first_name'] as String?,
      lastName: json['last_name'] as String?,
      age: json['age'] as int?,
      sex: json['sex'] as String?,
      weightKg: (json['weight_kg'] as num?)?.toDouble(),
      heightCm: (json['height_cm'] as num?)?.toDouble(),
      goal: json['goal'] as String?,
      activityLevel: json['activity_level'] as String?,
      dietaryPreferences: json['dietary_preferences'] as String?,
      notes: json['notes'] as String?,
    );
  }

  final String id;
  final String userId;
  final String? firstName;
  final String? lastName;
  final int? age;
  final String? sex;
  final double? weightKg;
  final double? heightCm;
  final String? goal;
  final String? activityLevel;
  final String? dietaryPreferences;
  final String? notes;

  Map<String, dynamic> toJson() {
    return {
      'first_name': firstName,
      'last_name': lastName,
      'age': age,
      'sex': sex,
      'weight_kg': weightKg,
      'height_cm': heightCm,
      'goal': goal,
      'activity_level': activityLevel,
      'dietary_preferences': dietaryPreferences,
      'notes': notes,
    };
  }
}

class NutritionTarget {
  const NutritionTarget({
    required this.id,
    required this.userId,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.waterMl,
    required this.fiberG,
    required this.sodiumMg,
  });

  factory NutritionTarget.fromJson(Map<String, dynamic> json) {
    return NutritionTarget(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      calories: json['calories'] as int,
      proteinG: json['protein_g'] as int,
      carbsG: json['carbs_g'] as int,
      fatG: json['fat_g'] as int,
      waterMl: json['water_ml'] as int,
      fiberG: json['fiber_g'] as int,
      sodiumMg: json['sodium_mg'] as int,
    );
  }

  final String id;
  final String userId;
  final int calories;
  final int proteinG;
  final int carbsG;
  final int fatG;
  final int waterMl;
  final int fiberG;
  final int sodiumMg;

  Map<String, dynamic> toJson() {
    return {
      'calories': calories,
      'protein_g': proteinG,
      'carbs_g': carbsG,
      'fat_g': fatG,
      'water_ml': waterMl,
      'fiber_g': fiberG,
      'sodium_mg': sodiumMg,
    };
  }
}
