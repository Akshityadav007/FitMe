import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';

class ApiClient {
  ApiClient({required AppConfig config, http.Client? httpClient})
    : _config = config,
      _httpClient = httpClient ?? http.Client();

  final AppConfig _config;
  final http.Client _httpClient;

  Future<Map<String, Object?>> getJson(
    String path, {
    String? authToken,
  }) async {
    final uri = Uri.parse('${_config.apiBaseUrl}$path');
    final response = await _httpClient.get(
      uri,
      headers: authToken == null ? null : {'Authorization': 'Bearer $authToken'},
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Expected a JSON object response.');
    }
    return decoded;
  }

  Future<Map<String, Object?>> postJson(
    String path,
    Map<String, dynamic> body, {
    String? authToken,
  }) async {
    final uri = Uri.parse('${_config.apiBaseUrl}$path');
    final response = await _httpClient.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: jsonEncode(body),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }

    if (response.body.isEmpty) {
      return <String, Object?>{};
    }
    final decoded = jsonDecode(response.body);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Expected a JSON object response.');
    }
    return decoded;
  }

  Future<Map<String, Object?>> putJson(
    String path,
    Map<String, dynamic> body, {
    String? authToken,
  }) async {
    final uri = Uri.parse('${_config.apiBaseUrl}$path');
    final response = await _httpClient.put(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: jsonEncode(body),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Expected a JSON object response.');
    }
    return decoded;
  }

  Future<List<Object?>> getJsonList(
    String path, {
    String? authToken,
  }) async {
    final uri = Uri.parse('${_config.apiBaseUrl}$path');
    final response = await _httpClient.get(
      uri,
      headers: authToken == null ? null : {'Authorization': 'Bearer $authToken'},
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! List<Object?>) {
      throw const FormatException('Expected a JSON array response.');
    }
    return decoded;
  }

  Future<Map<String, Object?>> postBytes(
    String path, {
    required List<int> body,
    required String contentType,
    String? authToken,
  }) async {
    final uri = Uri.parse('${_config.apiBaseUrl}$path');
    final response = await _httpClient.post(
      uri,
      headers: {
        'Content-Type': contentType,
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: body,
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! Map<String, Object?>) {
      throw const FormatException('Expected a JSON object response.');
    }
    return decoded;
  }

  Future<List<Object?>> postJsonList(
    String path,
    Map<String, dynamic> body, {
    String? authToken,
  }) async {
    final uri = Uri.parse('${_config.apiBaseUrl}$path');
    final response = await _httpClient.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: jsonEncode(body),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw ApiException(response.statusCode, response.body);
    }

    final decoded = jsonDecode(response.body);
    if (decoded is! List<Object?>) {
      throw const FormatException('Expected a JSON array response.');
    }
    return decoded;
  }
}

class ApiException implements Exception {
  const ApiException(this.statusCode, this.body);

  final int statusCode;
  final String body;

  @override
  String toString() => 'ApiException($statusCode): $body';
}
