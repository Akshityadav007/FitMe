import '../../core/network/api_client.dart';
import 'notification_models.dart';

class NotificationRepository {
  const NotificationRepository(this._apiClient);

  final ApiClient _apiClient;

  Future<List<NotificationItem>> fetchList({required String token}) async {
    final raw = await _apiClient.getJsonList('/notifications', authToken: token);
    return raw
        .map((item) => NotificationItem.fromJson(item as Map<String, Object?>))
        .toList();
  }

  Future<List<NotificationItem>> check({required String token}) async {
    final raw = await _apiClient.postJsonList('/notifications/check', const {}, authToken: token);
    return raw
        .map((item) => NotificationItem.fromJson(item as Map<String, Object?>))
        .toList();
  }

  Future<void> markRead({required String token, required String notificationId}) async {
    await _apiClient.postJson('/notifications/$notificationId/read', const {}, authToken: token);
  }
}
