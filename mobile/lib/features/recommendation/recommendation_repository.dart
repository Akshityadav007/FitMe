import '../../core/network/api_client.dart';
import 'recommendation_models.dart';

class RecommendationRepository {
  const RecommendationRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<Recommendation> recommend({
    required String token,
    required String date,
    String mealType = 'lunch',
  }) async {
    final json = await _apiClient.postJson(
      '/recommendations',
      {'date': date, 'meal_type': mealType},
      authToken: token,
    );
    return Recommendation.fromJson(json);
  }
}
