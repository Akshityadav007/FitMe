import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../auth/auth_providers.dart';
import 'notification_models.dart';
import 'notification_repository.dart';

final notificationRepositoryProvider = Provider<NotificationRepository>((ref) {
  return NotificationRepository(ref.watch(apiClientProvider));
});

final notificationsProvider = FutureProvider.autoDispose<List<NotificationItem>>((ref) {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  return ref.watch(notificationRepositoryProvider).fetchList(token: token);
});
