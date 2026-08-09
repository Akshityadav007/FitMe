import 'package:fitme/core/config/app_config.dart';
import 'package:fitme/core/network/api_client.dart';
import 'package:fitme/features/health/health_repository.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('fetchHealth parses the backend health contract', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(), 'http://example.test/api/v1/health');
      return http.Response(
        '{"status":"ok","service":"fitme-backend",'
        '"checked_at":"2026-08-09T09:00:00Z"}',
        200,
      );
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final repository = HealthRepository(apiClient);

    final health = await repository.fetchHealth();

    expect(health.status, 'ok');
    expect(health.service, 'fitme-backend');
    expect(
      health.checkedAt.toUtc().toIso8601String(),
      '2026-08-09T09:00:00.000Z',
    );
  });
}
