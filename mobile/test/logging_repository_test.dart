import 'dart:convert';

import 'package:fitme/core/config/app_config.dart';
import 'package:fitme/core/network/api_client.dart';
import 'package:fitme/features/daily/daily_repository.dart';
import 'package:fitme/features/notifications/notification_repository.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('logFood posts the food entry contract', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(), 'http://example.test/api/v1/daily/food');
      final body = jsonDecode(request.body) as Map<String, dynamic>;
      expect(body['date'], '2026-08-09');
      expect(body['meal_type'], 'lunch');
      expect(body['food_name'], 'Chicken rice bowl');
      expect(body['calories'], 620);
      return http.Response('{}', 200);
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    await DailyRepository(apiClient).logFood(
      token: 'token-123',
      date: '2026-08-09',
      mealType: 'lunch',
      foodName: 'Chicken rice bowl',
      calories: 620,
      proteinG: 45,
      carbsG: 55,
      fatG: 20,
    );
  });

  test('logSleep and logWorkout post the expected contracts', () async {
    final requests = <String>[];
    final client = MockClient((request) async {
      requests.add(request.url.path);
      return http.Response('{}', 200);
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final repo = DailyRepository(apiClient);
    await repo.logSleep(token: 't', date: '2026-08-09', durationMinutes: 420, quality: 4);
    await repo.logWorkout(token: 't', date: '2026-08-09', name: 'Upper body', durationMinutes: 60);

    expect(requests, contains('/api/v1/daily/sleep'));
    expect(requests, contains('/api/v1/daily/workout'));
  });

  test('notifications check parses the returned array', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(), 'http://example.test/api/v1/notifications/check');
      return http.Response(
        '[{"id":"n1","user_id":"u1","category":"hydration","title":"Drink water",'
        '"body":"Time for a glass.","created_at":"2026-08-09T09:00:00Z","read_at":null}]',
        200,
      );
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final items = await NotificationRepository(apiClient).check(token: 'token-123');

    expect(items, hasLength(1));
    expect(items.first.category, 'hydration');
    expect(items.first.readAt, isNull);
  });
}
