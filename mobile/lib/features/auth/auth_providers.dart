import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/config/app_config.dart';
import '../../core/network/api_client.dart';
import 'auth_models.dart';
import 'auth_repository.dart';
import 'session_storage.dart';

final appConfigProvider = Provider<AppConfig>((ref) => AppConfig.fromEnvironment);

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(config: ref.watch(appConfigProvider));
});

final sessionStorageProvider = Provider<SessionStorage>((ref) {
  return const SessionStorage();
});

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  return AuthRepository(ref.watch(apiClientProvider), ref.watch(sessionStorageProvider));
});

final authTokenProvider = FutureProvider<String?>((ref) {
  return ref.watch(authRepositoryProvider).readToken();
});

final profileProvider = FutureProvider.autoDispose<UserProfile>((ref) {
  final token = ref.watch(authTokenProvider).value;
  if (token == null) {
    throw StateError('Not authenticated.');
  }
  return ref.watch(authRepositoryProvider).fetchProfile(token);
});
