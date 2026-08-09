import '../../core/network/api_client.dart';
import 'progress_models.dart';

class ProgressRepository {
  const ProgressRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<WeeklyProgress> fetchWeekly({
    required String token,
    required String endDate,
  }) async {
    final json = await _apiClient.getJson('/progress/weekly?end_date=$endDate', authToken: token);
    return WeeklyProgress.fromJson(json);
  }
}
