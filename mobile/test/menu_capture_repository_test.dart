import 'package:fitme/core/config/app_config.dart';
import 'package:fitme/core/network/api_client.dart';
import 'package:fitme/features/menu_capture/menu_repository.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('upload posts raw bytes and parses the menu image contract', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(), 'http://example.test/api/v1/menu-images/upload');
      expect(request.headers['Content-Type'], 'image/jpeg');
      expect(request.headers['Authorization'], 'Bearer token-123');
      expect(request.bodyBytes, [1, 2, 3]);
      return http.Response(
        '{"id":"img-1","user_id":"u1","source":"camera","status":"pending","image_url":"/uploads/abc.jpg"}',
        200,
      );
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final image = await MenuCaptureRepository(apiClient)
        .upload(token: 'token-123', bytes: [1, 2, 3], contentType: 'image/jpeg');

    expect(image.id, 'img-1');
    expect(image.status, 'pending');
    expect(image.imageUrl, '/uploads/abc.jpg');
  });

  test('process parses the extracted items contract', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(),
          'http://example.test/api/v1/menu-images/img-1/process');
      return http.Response(
        '{"id":"img-1","status":"extracted","items":['
        '{"id":"it-1","menu_image_id":"img-1","name":"Chicken wrap",'
        '"estimated_calories":420,"estimated_protein_g":30,'
        '"estimated_carbs_g":40,"estimated_fat_g":15,"confidence":0.86}'
        ']}',
        200,
      );
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final result = await MenuCaptureRepository(apiClient)
        .process(token: 'token-123', menuImageId: 'img-1');

    expect(result.status, 'extracted');
    expect(result.items, hasLength(1));
    expect(result.items.first.name, 'Chicken wrap');
    expect(result.items.first.confidence, 0.86);
  });

  test('confirmItem posts the confirmation payload', () async {
    final client = MockClient((request) async {
      expect(request.url.toString(),
          'http://example.test/api/v1/menu-items/it-1/confirm');
      final body = request.body;
      expect(body, contains('"date":"2026-08-09"'));
      expect(body, contains('"meal_type":"lunch"'));
      expect(body, contains('"quantity_g":100'));
      return http.Response(
        '{"id":"e1","user_id":"u1","food_id":"f1","date":"2026-08-09",'
        '"meal_type":"lunch","quantity_g":100,"food_name":"Chicken wrap",'
        '"calories":420,"protein_g":30,"carbs_g":40,"fat_g":15}',
        200,
      );
    });

    final apiClient = ApiClient(
      config: const AppConfig(apiBaseUrl: 'http://example.test/api/v1'),
      httpClient: client,
    );
    final entry = await MenuCaptureRepository(apiClient).confirmItem(
      token: 'token-123',
      menuItemId: 'it-1',
      date: '2026-08-09',
      mealType: 'lunch',
      quantityG: 100,
    );

    expect(entry['food_name'], 'Chicken wrap');
    expect(entry['calories'], 420);
  });
}
