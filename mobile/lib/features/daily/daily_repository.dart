import '../../core/network/api_client.dart';
import 'daily_models.dart';

class DailyRepository {
  const DailyRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<DailySummary> fetchSummary({required String token, required String date}) async {
    final json = await _apiClient.getJson('/daily/summary?date=$date', authToken: token);
    return DailySummary.fromJson(json);
  }

  Future<NutritionTarget> fetchTargets({required String token}) async {
    final json = await _apiClient.getJson('/nutrition-targets/me', authToken: token);
    return NutritionTarget.fromJson(json);
  }

  Future<void> logWater({required String token, required String date, required int amountMl}) async {
    await _apiClient.postJson(
      '/daily/water',
      {'date': date, 'amount_ml': amountMl},
      authToken: token,
    );
  }

  Future<void> logWeight({required String token, required String date, required double weightKg}) async {
    await _apiClient.postJson(
      '/daily/weight',
      {'date': date, 'weight_kg': weightKg},
      authToken: token,
    );
  }

  Future<void> logSteps({required String token, required String date, required int steps}) async {
    await _apiClient.postJson(
      '/daily/steps',
      {'date': date, 'steps': steps},
      authToken: token,
    );
  }

  Future<void> logSleep({
    required String token,
    required String date,
    required int durationMinutes,
    int? quality,
  }) async {
    await _apiClient.postJson(
      '/daily/sleep',
      {
        'date': date,
        'duration_minutes': durationMinutes,
        if (quality != null) 'quality': quality,
      },
      authToken: token,
    );
  }

  Future<void> logWorkout({
    required String token,
    required String date,
    required String name,
    int? durationMinutes,
    String? notes,
  }) async {
    await _apiClient.postJson(
      '/daily/workout',
      {
        'date': date,
        'name': name,
        if (durationMinutes != null) 'duration_minutes': durationMinutes,
        if (notes != null) 'notes': notes,
      },
      authToken: token,
    );
  }

  Future<void> logFood({
    required String token,
    required String date,
    required String mealType,
    required String foodName,
    required int calories,
    required int proteinG,
    required int carbsG,
    required int fatG,
    String? notes,
  }) async {
    await _apiClient.postJson(
      '/daily/food',
      {
        'date': date,
        'meal_type': mealType,
        'food_name': foodName,
        'calories': calories,
        'protein_g': proteinG,
        'carbs_g': carbsG,
        'fat_g': fatG,
        if (notes != null) 'notes': notes,
      },
      authToken: token,
    );
  }
}
