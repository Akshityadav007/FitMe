import '../../core/network/api_client.dart';
import 'health_models.dart';

class HealthRepository {
  const HealthRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<HealthResponse> fetchHealth() async {
    final json = await _apiClient.getJson('/health');
    return HealthResponse.fromJson(json);
  }
}
