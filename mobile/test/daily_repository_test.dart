import 'package:fitme/core/config/app_config.dart';
import 'package:fitme/core/network/api_client.dart';
import 'package:fitme/features/daily/daily_repository.dart';
import 'package:fitme/features/recommendation/recommendation_repository.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('fetchSummary parses the daily summary contract', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(),
          'http://example.test/api/v1/daily/summary?date=2026-08-09');
      expect(request.headers['Authorization'], 'Bearer token-123');
      return http.Response(
        '{"date":"2026-08-09","weight_kg":73.2,"water_ml":750,'
        '"food_calories":620,"protein_g":45,"carbs_g":55,"fat_g":20,'
        '"steps":8200,"sleep_minutes":420,"workout_sessions":1}',
        200,
      );
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final summary = await DailyRepository(apiClient)
        .fetchSummary(token: 'token-123', date: '2026-08-09');

    expect(summary.foodCalories, 620);
    expect(summary.proteinG, 45);
    expect(summary.steps, 8200);
    expect(summary.sleepMinutes, 420);
    expect(summary.weightKg, 73.2);
  });

  test('recommend parses the structured recommendation contract', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(), 'http://example.test/api/v1/recommendations');
      return http.Response(
        '{"date":"2026-08-09","meal_type":"lunch",'
        '"targets":{"calories":2200,"protein_g":150,"carbs_g":250,"fat_g":60},'
        '"consumed":{"calories":620,"protein_g":45,"carbs_g":55,"fat_g":20},'
        '"remaining":{"calories":1580,"protein_g":105,"carbs_g":195,"fat_g":40},'
        '"recommendation":{"menu_item_id":"m1","name":"Chicken wrap",'
        '"calories":420,"protein_g":30,"carbs_g":40,"fat_g":15,"confidence":0.9},'
        '"alternatives":[],"reason":"High protein.","uncertainty":false,'
        '"uncertainty_reason":null,"suggested_action":"Order the wrap."}',
        200,
      );
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final recommendation = await RecommendationRepository(apiClient)
        .recommend(token: 'token-123', date: '2026-08-09');

    expect(recommendation.recommendation!.name, 'Chicken wrap');
    expect(recommendation.remaining.calories, 1580);
    expect(recommendation.uncertainty, isFalse);
  });
}
