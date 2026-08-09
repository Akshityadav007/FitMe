import '../../core/network/api_client.dart';
import 'coach_models.dart';

class CoachRepository {
  const CoachRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<CoachChatResponse> sendMessage({
    required String token,
    required String message,
    String? conversationId,
  }) async {
    final json = await _apiClient.postJson(
      '/coach/chat',
      {
        'message': message,
        if (conversationId != null) 'conversation_id': conversationId,
      },
      authToken: token,
    );
    return CoachChatResponse.fromJson(json);
  }
}
